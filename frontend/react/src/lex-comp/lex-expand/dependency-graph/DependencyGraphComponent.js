//imports
import './DependencyGraph.css'

//react
import React from 'react';
import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';
import GoDiagramWrapper from './GoDiagramWrapper';

//master export
export default class DependencyGraph extends React.Component {
  // console.warn(props);

  constructor(props){
    super(props);

    console.warn(this.links, this.node);

    this.state = {
      nodeDataArray: props.data.nodes,
      linkDataArray: props.data.links,
      modeldata: {
        canRelink: true
      },
      selectedKey: null,
      skipsDiagramUpdate: false
    };

    // bind handler methods
    this.handleDiagramEvent = this.handleDiagramEvent.bind(this);
    this.handleModelChange = this.handleModelChange.bind(this);
    this.handleRelinkChange = this.handleRelinkChange.bind(this);

    this.diagramRef = React.createRef();
    console.warn(this.diagramRef);
  }

  handleDiagramEvent(e) {
    const name = e.name;
    console.warn(e);
    switch (name) {
      case 'ChangedSelection': {
        const sel = e.subject.first();
        if (sel) {
          this.setState({ selectedKey: sel.key });
        } else {
          this.setState({ selectedKey: null });
        }
        break;
      }
      default: break;
    }
  }

  /**
   * Handle GoJS model changes, which output an object of data changes via Model.toIncrementalData.
   * This method should iterates over those changes and update state to keep in sync with the GoJS model.
   * This can be done via setState in React or another preferred state management method.
   * @param obj a JSON-formatted string
   */
  handleModelChange(obj) {
    const insertedNodeKeys = obj.insertedNodeKeys;
    const modifiedNodeData = obj.modifiedNodeData;
    const removedNodeKeys = obj.removedNodeKeys;
    const insertedLinkKeys = obj.insertedLinkKeys;
    const modifiedLinkData = obj.modifiedLinkData;
    const removedLinkKeys = obj.removedLinkKeys;
    const modifiedModelData = obj.modelData;

    console.log(obj);

    // see gojs-react-basic for an example model change handler
    // when setting state, be sure to set skipsDiagramUpdate: true since GoJS already has this update
  }

  /**
   * Handle changes to the checkbox on whether to allow relinking.
   * @param e a change event from the checkbox
   */
  handleRelinkChange(e) {
    const target = e.target;
    const value = target.checked;
    this.setState({ modelData: { canRelink: value }, skipsDiagramUpdate: false });
  }

  componentDidMount(){
    this.diagramRef.current.update();
  }

  render() {
    return (
      <div className='result-wrapper'>
        <GoDiagramWrapper
          ref={this.diagramRef}
          nodeDataArray={this.state.nodeDataArray}
          linkDataArray={this.state.linkDataArray}
          modelData={this.state.modelData}
          skipsDiagramUpdate={this.state.skipsDiagramUpdate}
          onDiagramEvent={this.handleDiagramEvent}
          onModelChange={this.handleModelChange}
        />
      </div>
    )
  }
  //return master object
  
}