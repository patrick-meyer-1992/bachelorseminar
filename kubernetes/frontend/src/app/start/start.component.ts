import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-start',
  templateUrl: './start.component.html',
  styleUrls: ['./start.component.css'],
})
export class StartComponent implements OnInit {
  availableConfigs: String[] = [];
  experimentId: string = '';
  selectedConfig: string = 'config1, config4';
  numVehicles: string = '10, 15, 25';
  iterations: string = '20';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      // .get<{ configs: String[] }>('http://localhost:8000'+'/configs/')
      .get<{ configs: String[] }>('http://api.domain.com'+'/configs/')
      .subscribe(
        (data) => {
          this.availableConfigs = data.configs;
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
  }

  // onConfigChange(event: Event): void {
  //   this.selectedConfig = (event.target as HTMLSelectElement).value;
  // }

  startSimulation(): void {
    const payload = {
      experiment_id: this.experimentId,
      repair_config_name: this.selectedConfig,
      num_vehicles: this.numVehicles,
      num_iterations: this.iterations,
    };

    // this.http.post('http://localhost:8000'+'/sim_jobs', payload).subscribe(
    this.http.post('http://api.domain.com'+'/sim_jobs', payload).subscribe(
      (response) => {
      console.log('Simulation started successfully:', response);
      },
      (error) => {
      console.error('Error starting simulation', error);
      }
    );
  }
}