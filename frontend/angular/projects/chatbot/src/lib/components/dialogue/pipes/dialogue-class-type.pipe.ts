import { Pipe, PipeTransform } from "@angular/core";
import { EDialogueType } from "../enums";

@Pipe({
    name: 'dialogueClassType'
})
export class DialogueClassTypePipe implements PipeTransform {
    public transform(_type: EDialogueType): string {
        return _type === EDialogueType.Query ? 'query' : 'response';
    }

}