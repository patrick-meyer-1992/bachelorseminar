import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as Plotly from 'plotly.js-dist';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css'],
})

export class ResultsComponent implements OnInit {
  selectedExperiment = '';
  availableExperiments: string[] = [];  
  selectedNumVehicles: number = 0;
  availableNumVehicles: number[] = [];
  selectedRepairConfig = '';
  availableRepairConfigs: string[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      // .get<{ experiments: string[] }>('http://localhost:8000/experiments/')
      .get<{ experiments: string[] }>('http://api.quantumshoe.duckdns.org/experiments/')
      .subscribe(
        (data) => {
          this.availableExperiments = data.experiments;
          this.selectedExperiment = this.availableExperiments[0];
          this.updateDropdowns()
          // this.fetchDataAndPlot(this.selectedExperiment);
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
  }

  // onExperimentChange(): void {
  //   this.updateDropdowns(this.selectedExperiment);
  // }

  updateDropdowns(): void {
    this.http
      .get<{ num_vehicles: number[], repair_config_name: string[] }>(
      `http://api.quantumshoe.duckdns.org/experiment_params/${this.selectedExperiment}`)
      .subscribe(
      (data) => {
        console.log("data:" + data)
        this.availableNumVehicles = data.num_vehicles;
        this.selectedNumVehicles = data.num_vehicles[0];
        this.availableRepairConfigs = data.repair_config_name;
        this.selectedRepairConfig = data.repair_config_name[0];
      },
      (error) => {
        console.error('Error fetching experiment details', error);
      }
      );
  }

  fetchDataAndPlot(): void {
    this.http
    .get(`http://api.quantumshoe.duckdns.org/plot_result/`, {
      params: {
      num_vehicles: this.selectedNumVehicles,
      repair_config_name: this.selectedRepairConfig,
      experiment_id: this.selectedExperiment
      }
    }).subscribe((data: any) => {
      const plotData = data.data.map((item: any) => ({
        x: item.x,
        y: item.y,
        mode: item.mode,
        name: item.name,
        type: item.type,
      }));

      const layout = {
        title: 'Anzahl Fahrzeuge pro Zustand',
        xaxis: { title: '' },
        yaxis: { title: '' },
      };
      Plotly.newPlot('plot', plotData, layout);
    });
  }
}