import { NgModule } from "@angular/core";
import { DialogueComponent } from "./dialogue.component";
import { DialogueClassTypePipe } from "./pipes";
import { CommonModule } from "@angular/common";

@NgModule({
    imports: [
        CommonModule
    ],
    declarations: [
        DialogueComponent,
        DialogueClassTypePipe
    ],
    exports: [
        DialogueComponent
    ]
})
export class DialogueComponentModule {

}