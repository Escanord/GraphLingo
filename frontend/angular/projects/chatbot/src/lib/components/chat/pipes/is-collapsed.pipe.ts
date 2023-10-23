import { Pipe, PipeTransform } from "@angular/core";
import { EChatState } from "../enums";

@Pipe({
    name: 'isCollapsed'
})
export class IsCollapsedPipe implements PipeTransform {
    public transform(_state: EChatState): boolean {
        return _state === EChatState.Collapsed;
    }
}