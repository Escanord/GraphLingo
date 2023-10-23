export default class S3Retreival {
  constructor(){
  }

  static jsonFrom(url){
    return new Promise(resolve => {
      fetch(url).then(res => {console.warn(res.body); return res.json()})
        .then(
          result => {
            console.warn(result);
            resolve(result);
          },
          error => {
            // Something went wrong;
            console.warn(error);
            resolve(error);
          }
        )
      }
    )
  }
}