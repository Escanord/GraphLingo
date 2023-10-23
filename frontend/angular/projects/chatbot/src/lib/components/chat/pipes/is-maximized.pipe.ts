import { Pipe, PipeTransform } from "@angular/core";
import { EChatState } from "../enums";

@Pipe({
    name: 'isMaximized'
})
export class IsMaximizedPipe implements PipeTransform {
    public transform (_state: EChatState): boolean {
        return _state === EChatState.Maximized;
    }
}