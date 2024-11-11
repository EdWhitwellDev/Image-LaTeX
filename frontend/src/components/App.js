
import React, { Component } from "react";
import {
  BrowserRouter,
  Routes,
  Route,

} from "react-router-dom";
import UploadImage from "./UploadImage"; // load the component
import DataSetBuilder from "./DatasetBuilder";


class App extends Component { // this is the main component that will be rendered, as with all react components it extends/inherits from the react Component class
  constructor(props) {
    super(props);
    this.state = { // the state allows for easy access and handling of data on a users device
      Map : null,
      Data : null,
      Latex: null,
    };
  }


  render() {
    return (
      <div>
        <BrowserRouter> {/* this is the router that allows for the user to navigate between pages/components */}
            <Routes>
              <Route path="/" element={<UploadImage />} /> {/* the path is the url that the user will type in to access the equation converter pages, note that there is only one url as i have decided to handle the "pages" within the components for reasons i will talk about there */}
              <Route path="/dataset" element={<DataSetBuilder />} /> {/* the path is the url that the user will type in to access the page */}
            </Routes>
          </BrowserRouter>
      </div>
    );
  }
}

export default App;