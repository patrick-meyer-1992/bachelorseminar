import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as Plotly from 'plotly.js-dist';

@Component({
  selector: 'app-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css'],
})

export class ResultsComponent implements OnInit {
  experiment: string = '';
  selectedExperiment = '';
  availableExperiments: string[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http
      // .get<{ experiments: string[] }>('http://localhost:8000/experiments/')
      .get<{ experiments: string[] }>('http://api.quantumshoe.duckdns.org/experiments/')
      .subscribe(
        (data) => {
          this.availableExperiments = data.experiments;
          this.selectedExperiment = this.availableExperiments[0];
          this.fetchDataAndPlot(this.selectedExperiment);
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
  }

  onExperimentChange(event: Event): void {
    this.fetchDataAndPlot((event.target as HTMLSelectElement).value);
  }

  fetchDataAndPlot(experiment: string): void {
    this.http
    // .get('http://localhost:8000/plot_result/test2').subscribe((data: any) => {
    .get(`http://api.quantumshoe.duckdns.org/plot_result/${experiment}`).subscribe((data: any) => {
      
      const plotData = data.data.map((item: any) => ({
        x: item.x,
        y: item.y,
        mode: item.mode,
        name: item.name,
        type: item.type,
      }));

      const layout = {
        title: 'Results Plot',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Value' },
      };
      Plotly.newPlot('plot', plotData, layout);
    });
  }
}