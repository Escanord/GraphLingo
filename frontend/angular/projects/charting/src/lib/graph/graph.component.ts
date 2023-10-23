import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, Input, OnChanges, OnInit, Renderer2, SimpleChange, SimpleChanges, ViewChild } from "@angular/core";
import * as d3 from 'd3';
import { IEdge, INode } from "./interfaces";

@Component({
    selector: 'charting-graph',
    templateUrl: 'graph.component.html'
})
export class GraphComponent implements OnInit, AfterViewInit, OnChanges {

    @Input()
    public nodes: INode[] = [];

    @Input()
    public edges: IEdge[] = [];

    @Input()
    public width: number = 1000;

    @Input()
    public height = 1000;

    // Graph values
    private _svg: any;
    private _viewRef: any;
    private _zoom: any;
    private _color = d3.scaleOrdinal(d3.schemeCategory10);

    // Graph elements
    private _simulation: any;
    private _link: any;
    private _linkText: any;
    private _linkTextShadow: any;
    private _linkRef: any;
    private _node: any;
    private _nodeText: any;

    private _currentNodes!: INode[];

    @ViewChild('GraphWrapper')
    private _graphWrapper!: ElementRef<HTMLDivElement>;

    constructor(
        public cd: ChangeDetectorRef,
        public renderer: Renderer2
    ) {

    }

    public ngOnInit(): void {
    }

    public ngAfterViewInit(): void {
        this.renderGraph();
    }

    public ngOnChanges(_changes: SimpleChanges): void {
        const _nodes: INode[] = [];
        const _edges: IEdge[] = [];
        let _updateSimulation: boolean = false;

        const _edgeChanges: SimpleChange = _changes['edges'];
        if (_edgeChanges.previousValue !== undefined) {
            _updateSimulation = true;
            this._simulation.stop();
            const _existing: IEdge[] = [];
            const _new: IEdge[] = [];

            this._linkRef.remove();

            // Add links
            this._linkRef = this._viewRef.append("g")
                .selectAll()
                .data(_edgeChanges.currentValue)
                .join("g");

            this._link = this._linkRef.append('line')
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .attr("stroke-width", 2);

            this._linkTextShadow = this._linkRef
                .append('text')
                .attr("fill", "none")
                .attr("stroke", "#eee")
                .attr("stroke-width", 3)
                .attr("x", 0)
                .attr("y", 0)
                .text((d: IEdge) => d.name);

            this._linkText = this._linkRef
                .append('text')
                .attr("x", 0)
                .attr("y", 0)
                .text((d: IEdge) => d.name);

            _edges.push(..._edgeChanges.currentValue)
        }

        // Handle nodes:
        const _nodeChanges: SimpleChange = _changes['nodes'];
        if (_nodeChanges.previousValue !== undefined) {
            _updateSimulation = true;
            this._simulation.stop();
            const _existing: INode[] = [];
            const _new: INode[] = [];

            const _existingIds: Map<string, INode> = new Map(_nodeChanges.previousValue.map((_node: INode) => [_node.id, _node]));

            _nodeChanges.currentValue.forEach((_node: any) => {
                // if (_existingIds.has(_node.id)) {
                const _selectedNode: any = _existingIds.get(_node.id);
                _node.x = _selectedNode?.x || this.width / 2;
                _node.y = _selectedNode?.y || this.height / 2;
                // Object.assign(_node, _existingIds.get(_node.id));
                // }

                _existing.push(_node)
            });

            d3.selectAll('.node').remove();

            this._node = this._viewRef.append("g")
                .selectAll("g")
                .data(_existing)
                .join("g")
                .attr("class", "node")
                .attr("x", (d: any) => d.x || null)
                .attr("y", (d: any) => d.y || null)
                .attr("transform", (d: any) => `translate(${d.x || 0},${d.y || 0})`);
            this._node.append('circle')
                .attr("fill", (d: INode) => this._color(d.group.toString()))
                .attr("stroke", "white")
                .attr("stroke-width", 1.5)
                .attr("r", 20);

            this._node.call(d3.drag()
                .on("start", this.dragstarted.bind(this))
                .on("drag", this.dragged.bind(this))
                .on("end", this.dragended.bind(this)));
            this._addNodeText();

            _nodes.push(..._existing);

        }

        if (_updateSimulation) {
            // Set simulation
            this._simulation = d3.forceSimulation(_nodes as d3.SimulationNodeDatum[])
                .force("link", d3.forceLink(_edges).id((d: any) => d.id).distance(150))
                .force("charge", d3.forceManyBody())
                .force("center", d3.forceCenter(this.width / 2, this.height / 2))
                .force("collision", d3.forceCollide().radius(() => 75))
                .force("x", d3.forceX().x(() => this.width / 2))
                .force("y", d3.forceY().y(() => this.height / 2))
                // .alpha(.1)
                .alphaDecay(.04)
                .velocityDecay(.75)
                .on("tick", this.ticked.bind(this));
        }

        console.warn(_changes);
    }

    public renderGraph(): void {
        this._currentNodes = this.nodes;

        const _boudingContainer: DOMRect = this._graphWrapper.nativeElement.getBoundingClientRect();
        this.width = _boudingContainer.width;
        this.height = _boudingContainer.height;

        d3.selectAll("svg").remove();
        this._createSvg();
        // Draw graph elements
        this._addLinks();
        this._addLinkText();
        this._addNodes();
        this._addNodeText();

        // Set simulation
        this._simulation = d3.forceSimulation(this.nodes as d3.SimulationNodeDatum[])
            .force("link", d3.forceLink(this.edges).id((d: any) => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(() => 75))
            .force("x", d3.forceX().x(() => this.width / 2))
            .force("y", d3.forceY().y(() => this.height / 2))
            .on("tick", this.ticked.bind(this));
    }

    public updateGraph(): void {

    }

    private _createSvg(): void {
        this._svg = d3.select('div#d3-target')
            .append('svg')
            .attr("style", "font: 16px sans-serif;")
            .attr("viewBox", [0, 0, this.width, this.height])
            .attr("text-anchor", "middle");

        this._viewRef = this._svg
            .append('g');

        this._zoom = d3.zoom()
            .on('zoom', this.zoomed.bind(this));
        
        this._svg.call(this._zoom);
    }

    private _addLinks(): void {
        this._linkRef = this._viewRef.append("g")
            .selectAll()
            .data(this.edges)
            .join("g");

        this._link = this._linkRef.append('line')
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 2);
    }

    private _addLinkText(): void {
        this._linkTextShadow = this._linkRef
            .append('text')
            .attr("fill", "none")
            .attr("stroke", "#eee")
            .attr("stroke-width", 3)
            .attr("x", 0)
            .attr("y", 0)
            .text((d: IEdge) => d.name);

        this._linkText = this._linkRef
            .append('text')
            .attr("x", 0)
            .attr("y", 0)
            .text((d: IEdge) => d.name);

    }

    private _addNodes(): void {
        this._node = this._viewRef.append("g")
            .selectAll("g")
            .data(this.nodes)
            .join("g")
            .attr("class", "node");
        this._node.append('circle')
            .attr("fill", (d: INode) => this._color(d.group.toString()))
            .attr("stroke", "white")
            .attr("stroke-width", 1.5)
            .attr("r", 20);

        this._node.call(d3.drag()
            .on("start", this.dragstarted.bind(this))
            .on("drag", this.dragged.bind(this))
            .on("end", this.dragended.bind(this)));
    }

    private _addNodeText() {
        this._nodeText = this._node
            .append("text")
            .attr("x", 0)
            .attr("y", -25)
            .attr("fill", "none")
            .attr("stroke", "#eee")
            .attr("stroke-width", 3)
            .text((d: INode) => d.name)

        this._node
            .append("text")
            .attr("x", 0)
            .attr("y", -25)
            .text((d: INode) => d.name)

    }

    /**
     * Helper method to find the middle between two nodes
     * @param _pos1 Position of one node
     * @param _pos2 Position of the other node
     * @returns The middle between those two vectors.
     */
    private _halfDifference(_pos1: number, _pos2: number): number {
        const _smaller: number = Math.min(_pos1, _pos2);
        const _larger: number = Math.max(_pos1, _pos2);

        const _diff: number = (_larger - _smaller) / 2;

        return _smaller + _diff;
    }

    // Reheat the simulation when drag starts, and fix the subject position.
    public dragstarted(event: any) {
        if (!event.active) this._simulation.alphaTarget(.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag.
    public dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends.
    // Unfix the subject position now that it’s no longer being dragged.
    public dragended(event: any) {
        if (!event.active) this._simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    public zoomed(event: any) {
        this._viewRef.attr('transform', event.transform);
    }

    // On tick update positioning
    public ticked(): void {
        // Move the link
        if (this._link.length !== 0) {
            this._link
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            // Move link text
            this._linkText
                .attr("x", (d: any) => this._halfDifference(d.source.x, d.target.x))
                .attr("y", (d: any) => this._halfDifference(d.source.y, d.target.y));
            this._linkTextShadow
                .attr("x", (d: any) => this._halfDifference(d.source.x, d.target.x))
                .attr("y", (d: any) => this._halfDifference(d.source.y, d.target.y));
        }

        // Move the node
        d3.selectAll('.node').attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    }

}