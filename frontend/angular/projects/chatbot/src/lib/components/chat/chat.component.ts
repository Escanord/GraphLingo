import { ChangeDetectorRef, Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from "@angular/core";
import { ChatbotService, QueryService } from "../../services";
import { EDialogueType } from "../dialogue/enums";
import { EChatState } from "./enums";
import { IChatResponse, IGraphData } from "../../services/query/interfaces";
import { isNullOrUndefined } from "../../functions";
import { IEdge, INode } from "projects/charting/src/lib/graph/interfaces";
import { GraphComponent } from "projects/charting/src/public-api";
import { MatMenuModule } from '@angular/material/menu';

//an interface for all the databases
interface Database {
    value: string;
    viewValue: string;
}

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

    //declare the list of databases available
    public databases: Database[] = [
        {value: 'gpt', viewValue: 'Curriculum KG'},
        {value: 'crux', viewValue: 'Materials Science KG'},
        {value: 'prime', viewValue: 'Drugs KG'}
      ];
    
    //datbase name to pass onto backend/GraphLingo/views.py
    private db: string = "neo4j";

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

    //the method to switch between databases
    public toggleDatabase(value: string): string {

        //Later when it's not hardcoded, find the value directly from databases and parse it into a string
        //then return the the viewValue. The switch statement is temporary.
        switch(value) {
            //GPT
            case this.databases[0].value:
                // 
                this.db = this.databases[0].value                
                

                return this.databases[0].viewValue;

            //CRUX
            case this.databases[1].value:
                // 
                this.db = this.databases[1].value

                return this.databases[1].viewValue; 

            //Prime
            case this.databases[2].value:
                // 
                this.db = this.databases[2].value

                return this.databases[2].viewValue; 

            default:
                this.db = "neo4j"
                return "Default Database"
        }

        return "Something's wrong";
    }

    public sendQuery(_query?: string, _isFollowup: boolean = false): void {
        let _userQuery: string;
        const _queryData: any = {
            isFollowup: _isFollowup,
            explorativeRate: this.explorativeRate,
            //toggle database
            database: this.db
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