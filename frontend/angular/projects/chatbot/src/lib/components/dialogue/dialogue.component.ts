import { Component, EventEmitter, Input, Output } from "@angular/core";
import { EDialogueType } from "./enums";

@Component({
    selector: 'app-dialogue',
    templateUrl: './dialogue.component.html',
    styleUrls: ['./dialogue.component.scss']
})
export class DialogueComponent {
    @Input()
    public dialogueType!: EDialogueType;

    @Input()
    public text!: string;

    @Input()
    public data: any

    @Input()
    public isDisabled: boolean = false;

    @Output()
    public suggestionSelected: EventEmitter<string> = new EventEmitter();

    public selectSuggestion(_suggestion: string): void {
        if (this.isDisabled)
            return;

        this.suggestionSelected.emit(_suggestion);
    }

}
