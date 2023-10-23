import { EDialogueType } from "../enums";

export interface IDialogue {
    type: EDialogueType;
    text: string;
    data?: any;
}