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
      .get<{ experiments: string[] }>('http://localhost:8000/experiments/')
      .subscribe(
        (data) => {
          this.availableExperiments = data.experiments;
          this.selectedExperiment = this.availableExperiments[0];
        },
        (error) => {
          console.error('Error fetching configurations', error);
        }
      );
    this.fetchDataAndPlot();

  }

  onExperimentChange(event: Event): void {
    this.selectedExperiment = (event.target as HTMLSelectElement).value;
    console.log('Selected experiment:', this.selectedExperiment);
    this.fetchDataAndPlot();
  }

  fetchDataAndPlot(): void {
    this.http.get('http://localhost:8000/plot_result/test2').subscribe((data: any) => {
      console.log(data)
      console.log(data.data);
      console.log('Attributes of data:', Object.keys(data));
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
      console.log('Plotting...');
      Plotly.newPlot('plot', plotData, layout);
    });
  }
}