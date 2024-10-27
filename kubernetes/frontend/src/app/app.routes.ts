import { Routes } from '@angular/router';
import { ConfigurationComponent } from './configuration/configuration.component';
import { StartComponent } from './start/start.component';
import { ResultsComponent } from './results/results.component';

export const routes: Routes = [
  { path: 'configuration', component: ConfigurationComponent },
  { path: 'start', component: StartComponent },
  { path: 'results', component: ResultsComponent },
  { path: '', redirectTo: '/start', pathMatch: 'full' },
];
