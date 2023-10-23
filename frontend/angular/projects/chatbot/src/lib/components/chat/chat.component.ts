import { ChangeDetectorRef, Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from "@angular/core";
import { ChatbotService, QueryService } from "../../services";
import { EDialogueType } from "../dialogue/enums";
import { EChatState } from "./enums";
import { IChatResponse, IGraphData } from "../../services/query/interfaces";
import { isNullOrUndefined } from "../../functions";
import { IEdge, INode } from "projects/charting/src/lib/graph/interfaces";
import { GraphComponent } from "projects/charting/src/public-api";

@Component({
    selector: 'chat',
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.scss'],
    providers: [
        ChatbotService
    ]
})
export class ChatComponent implements OnInit {

    // Bot:
    public botResponding: boolean = false;

    // Graph:
    public hasGraph: boolean = false;

    public graphEdges: IEdge[] = [];

    public graphNodes: INode[] = [];

    @ViewChild('UserQueryInput')
    private _userQueryInput!: ElementRef;

    @ViewChild('ChatBody')
    private _chatBody!: ElementRef<HTMLDivElement>;

    @ViewChildren(GraphComponent)
    private _graphComponent!: QueryList<GraphComponent>;

    public explorativeRate: number = .5;

    EDialogueType = EDialogueType;

    public chatState: EChatState = EChatState.Maximized;

    public settingsState: EChatState = EChatState.Collapsed;

    constructor(
        public chatbotService: ChatbotService,
        public queryService: QueryService,
        public cd: ChangeDetectorRef
    ) { }

    ngOnInit(): void {
    }

    public openChat(): void {
        this.chatState = EChatState.Expanded;
    }

    public closeChat(): void {
        this.chatState = EChatState.Collapsed;
    }

    public expandChat(): void {
        this.chatState = EChatState.Maximized;
    }

    public minimizeChat(): void {
        this.chatState = EChatState.Collapsed;
    }

    public toggleChatMaximization(): void {
        this.chatState = this.chatState === EChatState.Maximized ? EChatState.Expanded : EChatState.Maximized;
    }

    public toggleChatSettings(): void {
        this.settingsState = this.settingsState === EChatState.Collapsed ? EChatState.Expanded : EChatState.Collapsed;
    }

    public sendQuery(_query?: string, _isFollowup: boolean = false): void {
        let _userQuery: string;
        const _queryData: any = {
            isFollowup: _isFollowup,
            explorativeRate: this.explorativeRate
        };

        // Add custom query
        if (isNullOrUndefined(_query)) {
            const _nativeElement: HTMLInputElement = this._userQueryInput.nativeElement;
            _userQuery = _nativeElement.value;

            _nativeElement.value = '';
        }
        else {
            _userQuery = _query
        }

        this.chatbotService.addUserQuery(_userQuery);
        setTimeout(() => {
            this._scrollChatBottom();
        })

        this.botResponding = true;
        this.queryService.submit({
            msg: _userQuery,
            data: _queryData
        }).subscribe({
            next: (_response: IChatResponse) => {
                this.botResponding = false;
                this.chatbotService.addBotResponse(_response.msg, _response.data);

                // Graph rendering
                this._renderGraph(_response?.data?.graph);
                setTimeout(() => {
                    this._scrollChatBottom();
                })
            },
            error: (_error: any) => {
                this.botResponding = false;
                this.chatbotService.addBotResponse('I\'m sorry, there was a error connecting with my brain. Please try again later!')
            }
        });
    }

    private _renderGraph(_graphData: IGraphData): void {
        if (!isNullOrUndefined(_graphData)) {
            this.expandChat();
            this.hasGraph = true;
            this.graphEdges = _graphData.edges;
            this.graphNodes = _graphData.nodes;
            
            this.cd.detectChanges();
            // this._graphComponent.first.renderGraph();
        }
        else {
            this.hasGraph = false;
        }
    }

    private _scrollChatBottom(): void {
        this._chatBody.nativeElement.scrollTop = this._chatBody.nativeElement.scrollHeight;
    }

    public sliderDisplay(_value: number): string {
        return _value.toString();
    }

    public monitorKeypresses(_inputEvent: KeyboardEvent): void {
        switch (_inputEvent.code) {
            case 'Enter':
                this.sendQuery();
                _inputEvent.preventDefault();
                break;
        }
    }
}