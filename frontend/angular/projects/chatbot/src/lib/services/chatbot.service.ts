import { Injectable } from '@angular/core';
import { IDialogue } from '../components/dialogue';
import { EDialogueType } from '../components/dialogue/enums';
import { cloneDeep } from 'lodash';

@Injectable()
export class ChatbotService {

  constructor() { }

  private get DEFAULT_PROMPT(): IDialogue {
    return cloneDeep({
      type: EDialogueType.Response,
      text: 'How can I help you?'
    });
  }

  private _dialogueHistory: IDialogue[] = [
    this.DEFAULT_PROMPT
  ];

  public get history(): IDialogue[] {
    return this._dialogueHistory;
  }

  public addUserQuery(_text: string, _data?: any): void {
    this._addResponse(EDialogueType.Query, _text, _data);
  }

  public addBotResponse(_text: string, _data?: any): void {
    this._addResponse(EDialogueType.Response, _text, _data);
  }

  private _addResponse(_type: EDialogueType, _text: string, _data?: any): void {
    const _dialogue: IDialogue = {
      type: _type,
      text: _text
    }

    if (_data !== undefined || _data !== null) {
      _dialogue.data = _data;
    }

    this._dialogueHistory.push(_dialogue);
  }

  public reset(): void {
    this._dialogueHistory.length = 0;
    this._dialogueHistory.push(this.DEFAULT_PROMPT);
  }
}
