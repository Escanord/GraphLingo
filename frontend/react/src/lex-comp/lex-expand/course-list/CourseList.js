//imports
import './CourseList.css'

//react
import React from 'react';

//master export
export default function CourseList(props) {
  const courses = props.courses

  // Allow for showing hidden descriptions.
  let toggleDisplay = (e) => {
    const target_node = e.target.parentNode.nextElementSibling
    let displayProp = getComputedStyle(target_node).display;
    target_node.style.display = displayProp == "none" ? "revert" : "none";
  }

  //return master object
  return (
    <div className='result-wrapper'>
      <table id="result">
        <thead>
          <tr>
              <th>Department</th>
              <th>Code</th>
              <th>Course Title</th>
              <th>Credits</th>
          </tr>
        </thead>
        <tbody>
          {courses.map((course, index) => 
          (<React.Fragment key={index}>
            <tr className="row-result" onClick={(e)=>{
                  toggleDisplay(e);}
                }>
              <td className="tc-one">{course.departmentID}</td>
              <td className="tc-two">{course.code}</td>
              <td className="tc-three">{course.name}</td>
              <td className="tc-four">{course.credit}</td>
            </tr>
            <tr className="res-desc-wrapper">
                <td className="res-desc" colSpan="4">{course.description}</td>
            </tr>
          </React.Fragment>))}
        </tbody>
    </table>
  </div>)
}