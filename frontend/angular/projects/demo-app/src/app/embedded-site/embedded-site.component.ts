import { AfterViewInit, Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';

@Component({
  selector: 'app-embedded-site',
  templateUrl: './embedded-site.component.html',
  styleUrls: ['./embedded-site.component.scss']
})
export class EmbeddedSiteComponent implements AfterViewInit {
  @Input()
  public silence: boolean = false;

  constructor() { }

  public ngAfterViewInit(): void {
  }

}
