import { NgModule } from "@angular/core";
import { FormsModule } from '@angular/forms';
import { MatIconModule } from "@angular/material/icon";
import { MatSliderModule } from '@angular/material/slider';
import { BrowserModule } from "@angular/platform-browser";
import { GraphComponentModule } from "projects/charting/src/lib/graph";
import { DialogueComponentModule } from "../dialogue";
import { EllipsisComponentModule } from "../ellipsis";
import { ChatComponent } from "./chat.component";
import { IsCollapsedPipe, IsMaximizedPipe } from "./pipes";
import {MatMenuModule} from '@angular/material/menu';
import {MatCheckboxModule} from '@angular/material/checkbox';

const _pipes = [
    IsCollapsedPipe,
    IsMaximizedPipe
]

const _angularMaterial = [
    MatSliderModule
]

@NgModule({
    imports: [
        _angularMaterial,
        FormsModule,
        BrowserModule,
        MatIconModule,
        DialogueComponentModule,
        GraphComponentModule,
        EllipsisComponentModule,
        MatMenuModule, MatCheckboxModule
    ],
    declarations: [
        ChatComponent,
        _pipes
    ],
    exports: [
        ChatComponent
    ]
})
export class ChatModule {

}