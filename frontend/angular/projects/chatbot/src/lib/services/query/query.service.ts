import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { delay, map } from "rxjs/operators";
import { IChatResponse } from "./interfaces";

@Injectable({
    providedIn: 'root'
})
export class QueryService {

    private get API_ROOT(): string {
        return 'http://localhost:8000/GraphLingo/dialog/'
    }

    constructor(private _http: HttpClient) {

    }
    public submit(_request: IChatResponse): Observable<IChatResponse> {
        const _body: string = JSON.stringify(_request);

        // return of({
        //     msg: 'My Response',
        //     data: {
        //         suggestions: [
        //             'Suggestion 1',
        //             'Suggestion 2'
        //         ],
        //         triples: [
        //             ['Node1', 'Rel1', 'Node2'],
        //             ['Node2', 'Rel2', 'Node3']
        //         ],
        //         graph: {
        //             nodes: [
        //                 { name: 'Node 1', id: 'Node1', group: 1 },
        //                 { name: 'Node 2', id: 'Node2', group: 2 },
        //                 { name: 'Node 3', id: 'Node3', group: 2 },
        //                 { name: 'Node 4', id: 'Node4', group: 3 },
        //                 { name: 'Node 5', id: 'Node5', group: 3 },
        //                 { name: 'Node 6', id: 'Node6', group: 4 },
        //                 { name: 'Node 7', id: 'Node7', group: 5 },
        //             ],
        //             edges: [
        //                 { name: 'Link 1', source: 'Node1', target: 'Node2' },
        //                 { name: 'Link 2', source: 'Node2', target: 'Node3' },
        //                 { name: 'Link 3', source: 'Node5', target: 'Node6' },
        //             ]
        //         }
        //     }
        // }).pipe(delay(3000))

        return this._http.post<IChatResponse>(this.API_ROOT, _body, {
            headers: {
                'content-type': 'application/json'
            }
        }).pipe(map((_response: IChatResponse) => {
            _response.msg = _response.msg.trim();
            return _response;
        }));
    }
}