# Image-LaTeX Converter

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)  
*A project for my AQA NEA.*

---

The **Image-LaTeX Converter** allows users to upload an image of an equation and returns the corresponding LaTeX code. Additional features include:  
- Commenting on previously seen equations.  
- An API to extract images of uploaded equations and sub-images of characters, along with their labels as confirmed by a user.

---

## 📋 Features
1. **Image to LaTeX Conversion**: Upload an image of an equation and get the LaTeX output.  
2. **Character-Level Image Recognition**: Utilize convolutional neural networks (CNNs) to identify individual characters in equations.  
3. **API Integration**:  
   - Retrieve images of uploaded equations.  
   - Extract sub-images of characters with their associated labels.  
4. **Commenting System**: Keep track of previously analyzed equations.  

---

## 🚧 Limitations and Learnings
This project was my first attempt at combining Django, React, and machine learning techniques. While it successfully met the project requirements, it comes with a few caveats:  

1. **Rudimentary Image Recognition**:  
   - A custom CNN was developed from scratch without the use of frameworks like TensorFlow or PyTorch.  
   - Due to limited computational power, and basic implementation, the CNN could only identify one character at a time opposed to a object detection algorithm that could lable all characters in the image.  
   - Multiple networks were required to cover different character sets, requiring manual user categorization.  

2. **Development Context**:  
   - As my first large-scale project, the architecture and code styling reflect my learning curve.  
   - The image recognition component, though functional, is not suitable for a real world product, in any context other than my NEA, using more powerful libaries like tensorflow or pytorch would be an obvious choice, however this would have impacted my grade.

---

## 🛠️ Future Improvements
While the current implementation has limitations, the core concept is viable with the following changes:  
- Implementing larger, more advanced networks (utilizing TensorFlow or PyTorch).  
- Automating the character categorization process.  

Despite these limitations, the project has been an invaluable learning experience. It taught me:  
- **Web Development**: Integrating Django and React.  
- **Artificial Intelligence**: Building and training neural networks.  
- **Project Management**: Designing and executing a large-scale project.  

---

## 🚀 Outcome
The **Image-LaTeX Converter** achieved its primary goal and served as a stepping stone for my learning. Notably:  
- Providing an excellent into to deep learning and web developement.  
- Earning an **A** grade for my AQA NEA.
