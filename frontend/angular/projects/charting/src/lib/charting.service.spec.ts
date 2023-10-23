import { TestBed } from '@angular/core/testing';

import { ChartingService } from './charting.service';

describe('ChartingService', () => {
  let service: ChartingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChartingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
