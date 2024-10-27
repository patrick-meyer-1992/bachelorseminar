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

@Component({
  selector: 'app-configuration',
  standalone: false,
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
})
export class ConfigurationComponent implements OnInit {
  config: RepairFacility[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchConfiguration().subscribe((data: RepairFacility[]) => {
      this.config = data;
    });
  }

  fetchConfiguration(): Observable<RepairFacility[]> {
    return this.http.get<RepairFacility[]>(
      // 'http://fastapi-service.default.svc.cluster.local'
      'http://localhost:8000'
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
  }
}
