import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Worker {
  id: number;
  type: string;
  repair_rate_mean: number;
  repair_rate_sd: number;
}

interface Workspace {
  id: number;
  type: string;
  children: Worker[];
}

interface RepairFacility {
  id: number;
  type: string;
  children: Workspace[];
}

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit {
  config: RepairFacility[] = [];
  availableConfigNames: string[] = [];
  selectedConfigName: string = '';
  newConfigName: string = '';
  num_facilities: number = 0;
  num_workspaces: number = 0;
  num_workers: number = 0;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<{ configs: string[] }>('http://api.domain.com/configs/')
      .subscribe(
        (data) => {
          this.availableConfigNames = data.configs;
          this.selectedConfigName = this.availableConfigNames[0];
          this.initConfig(this.selectedConfigName);
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
  }

  initConfig(config_name: string): void {
    this.http.get<{ config: RepairFacility[] }>(
        `http://api.domain.com/config/${config_name}`
      )
      .subscribe(
        (data) => {
          this.config = data.config;
        },
        (error) => {
          console.error('Error fetching configuration data', error);
        }
      );
  }

  onConfigChange(event: Event): void {
    const selectedName = (event.target as HTMLSelectElement).value;

    this.http.get<{ config: RepairFacility[] }>(
        `http://api.domain.com/config/${selectedName}`
      )
      .subscribe(
        (data) => {
          this.config = data.config;
        },
        (error) => {
          console.error('Error fetching configuration data', error);
        }
      );
  }

  addFacility() {
    this.num_facilities += 1;
    this.config.push({
      // id: this.config.length + 1,
      id: this.num_facilities,
      type: 'repair_facility',
      children: [],
    });
  }

  removeFacility(index: number) {
    this.num_facilities -= 1;
    this.config.splice(index, 1);
  }

  addWorkspace(facilityIndex: number) {
    this.num_workspaces += 1;
    this.config[facilityIndex].children.push({
      id: this.num_workspaces,
      type: 'workspace',
      children: [],
    });
  }

  removeWorkspace(facilityIndex: number, workspaceIndex: number) {
    this.num_workspaces -= 1;
    this.config[facilityIndex].children.splice(workspaceIndex, 1);
  }

  addWorker(facilityIndex: number, workspaceIndex: number) {
    this.num_workers += 1;
    this.config[facilityIndex].children[workspaceIndex].children.push({
      id: this.num_workers,
        // this.config[facilityIndex].children[workspaceIndex].children.length + 1,
      type: 'worker',
      repair_rate_mean: 0,
      repair_rate_sd: 0
    });
  }

  removeWorker(
    facilityIndex: number,
    workspaceIndex: number,
    workerIndex: number
  ) {
    this.config[facilityIndex].children[workspaceIndex].children.splice(
      workerIndex,
      1
    );
    this.num_workers -= 1;
  }

  onSubmit() {
    this.http.post(`http://api.domain.com/add_config/${this.newConfigName}`, {
        name: this.newConfigName,
        config: this.config,
        })
      .subscribe(
      (response) => {
        console.log('Configuration successfully saved:', response);
      },
      (error) => {
        console.error('Error saving configuration', error);
      }
      );
  }
}
