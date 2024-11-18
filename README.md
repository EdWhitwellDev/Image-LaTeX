Image-LaTeX Converter

A project for my AQA NEA.

The Image-LaTeX Converter allows users to upload an image of a mathematical equation and returns the corresponding LaTeX code. Additional features include:

Commenting on previously seen equations.
An API to extract images of uploaded equations and sub-images of characters, along with their labels.
📋 Features
Image to LaTeX Conversion: Upload an image of an equation and get the LaTeX output.
Character-Level Image Recognition: Utilize convolutional neural networks (CNNs) to identify individual characters in equations.
API Integration:
Retrieve images of uploaded equations.
Extract sub-images of characters with their associated labels.
Commenting System: Keep track of previously analyzed equations.
🚧 Limitations and Learnings
This project was my first attempt at combining Django, React, and machine learning techniques. While it successfully met the project requirements, it comes with a few caveats:

Rudimentary Image Recognition:

A custom CNN was developed from scratch without the use of frameworks like TensorFlow or PyTorch.
Due to limited computational power, the CNN could only identify one character at a time.
Multiple networks were required to cover different character sets, necessitating manual user categorization.
Development Context:

As my first large-scale project, the architecture and code styling reflect my learning curve.
The image recognition component, though functional, highlights the need for a more robust neural network.
🛠️ Future Improvements
While the current implementation has limitations, the core concept is scalable with the following changes:

Implementing larger, more advanced networks (e.g., TensorFlow or PyTorch).
Automating the character categorization process.
Despite these limitations, the project has been an invaluable learning experience. It taught me:

Web Development: Integrating Django and React.
Artificial Intelligence: Building and training neural networks.
Project Management: Designing and executing a large-scale project.
🚀 Outcome
The Image-LaTeX Converter achieved its primary goal and served as a stepping stone for my learning. Notably:

It was a significant milestone in my journey as a developer.
The project also earned me an A.
