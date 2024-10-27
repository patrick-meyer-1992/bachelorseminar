import { Component } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(private router: Router) {}

  onTabChange(event: any) {
    const tabIndex = event.index;
    if (tabIndex === 0) {
      this.router.navigate(['/configuration']);
    } else if (tabIndex === 1) {
      this.router.navigate(['/start']);
    } else if (tabIndex === 2) {
      this.router.navigate(['/results']);
    }
  }
}
