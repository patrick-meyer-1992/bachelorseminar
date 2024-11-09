import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Worker {
  id: number;
  type: string;
  repair_rate: number;
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

interface Config {
  id: number;
  name: string;
}

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit {
  config: RepairFacility[] = [];
  availableConfigs: string[] = [];
  selectedConfig: string = '';
  configName: string = '';
  num_facilities: number = 0;
  num_workspaces: number = 0;
  num_workers: number = 0;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      .get<{ configs: string[] }>('http://localhost:8000/configs/')
      .subscribe(
        (data) => {
          this.availableConfigs = data.configs;
          this.selectedConfig = this.availableConfigs[0];
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
  }

  onConfigChange(event: Event): void {
    const selectedName = (event.target as HTMLSelectElement).value;
    console.log('Selected configuration:', selectedName);

    this.http
      .get<{ config: RepairFacility[] }>(
        `http://localhost:8000/config/${selectedName}`
      )
      .subscribe(
        (data) => {
          console.log('Fetched configuration data:', data);
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
      repair_rate: 0,
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
    console.log('Configuration saved:', this.config);
    console.log('Configuration name:', this.configName);
    this.http
      .post(`http://localhost:8000/add_config/${this.configName}`, {
      name: this.configName,
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
