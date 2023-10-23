import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmbeddedSiteComponent } from './embedded-site.component';

describe('EmbeddedSiteComponent', () => {
  let component: EmbeddedSiteComponent;
  let fixture: ComponentFixture<EmbeddedSiteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EmbeddedSiteComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EmbeddedSiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
