//imports
import './LexExpand.css'

//react
import React from 'react';
import CourseList from './course-list/CourseList';
import DependencyGraph from './dependency-graph/DependencyGraphComponent';

//master export
export default function LexExpand(props) {
  let expansionData = props.data;
  const [state] = React.useState(Date.now());
  console.warn("RERENDER");

  // Catalogue for all possible expansion items
  let types = {
    "course_list": (index, expansion) => (
      <CourseList
        key = {index}
        courses={expansion['data']}/>),
    "dep_graph": (index, expansion) => (
      <DependencyGraph
        key = {index}
        updated = {Date.now()}
        data={expansion['data']}/>)
  }

  //return master object
  return (
    <React.Fragment key = {state}>
    {expansionData ? expansionData.map((expansion, index) => 
      types[expansion['type']](index, expansion)
    ) : null}
    </React.Fragment>)
}