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
  availableConfigs: String[] = [];
  selectedConfig: string = '';
  configName: string = '';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      .get<{ configs: String[] }>('http://localhost:8000/get_configs/')
      .subscribe(
        (data) => {
          console.log('Fetched configurations:', data);
          this.availableConfigs = data.configs;
          console.log('Available configurations:', this.availableConfigs);
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
        `http://localhost:8000/get_config/${selectedName}`
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
    this.config.push({
      id: this.config.length + 1,
      type: 'repair_facility',
      children: [],
    });
  }

  removeFacility(index: number) {
    this.config.splice(index, 1);
  }

  addWorkspace(facilityIndex: number) {
    this.config[facilityIndex].children.push({
      id: this.config[facilityIndex].children.length + 1,
      type: 'workspace',
      children: [],
    });
  }

  removeWorkspace(facilityIndex: number, workspaceIndex: number) {
    this.config[facilityIndex].children.splice(workspaceIndex, 1);
  }

  addWorker(facilityIndex: number, workspaceIndex: number) {
    this.config[facilityIndex].children[workspaceIndex].children.push({
      id:
        this.config[facilityIndex].children[workspaceIndex].children.length + 1,
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
  }

  onSubmit() {
    console.log('Configuration saved:', this.config);
    console.log('Configuration name:', this.configName);
  }
}
