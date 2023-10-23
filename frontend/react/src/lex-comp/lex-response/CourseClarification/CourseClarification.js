import './CourseClarification.css';

export default function CourseClarification(props){
  const courses = props.courses;
  console.warn(courses);

  const callback = props.responseCallback;
  
  return <div className="clarification-list">
    {courses.map((course, index) => {
      return <span 
        key={index} 
        className="course-option"
        title={course["name"]}
        onClick={() => {callback(`${course["departmentID"]} ${course["code"]}`, course['courseID'].toString())}}>
          {`${course["departmentID"]} ${course["code"]}`}
        </span>
    })}
  </div>
}