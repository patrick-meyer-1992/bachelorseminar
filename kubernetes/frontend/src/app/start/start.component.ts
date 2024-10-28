import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-start',
  templateUrl: './start.component.html',
  styleUrls: ['./start.component.css'],
})
export class StartComponent implements OnInit {
  availableConfigs: String[] = [];
  selectedConfig: string = '';
  numVehicles: number = 100;
  iterations: number = 20;

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
    this.selectedConfig = (event.target as HTMLSelectElement).value;
    console.log('Selected configuration:', this.selectedConfig);
  }

  startSimulation(): void {
    console.log('Starting simulation with config:', this.selectedConfig);
    console.log('Number of vehicles:', this.numVehicles);
    console.log('Iterations:', this.iterations);
    // Add logic to start the simulation
  }
}