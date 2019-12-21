# A Simple Problem of Delivery
A project of Engineering Optimization

### 1. Environment
python 3.7+
pygame，numpy

## 2. How to use
#### 2.1 Initial the problem:
You can just run the problem_generator.py to generator an Simple Delivery problem with default parameters.
If you want to try a customized problem, you can run this program with parameters as follows:
```bash
python problem_generator.py \
    --port 5 \ #The number of the origins.
    --site 5 \ #The number of the destinies.
    --goods 50 \ # The number of goods in every port.
    --size 21 \ # The map size of the problem.
```
But you can just visualize the defualt problem in this project.
#### 2.2 Get the optimal solution
After you initial the problem, you can run the problem_solver.py to solve your problem. And the best solution you find will be saved in the database named record.db (This can be used for visualization.)And the best solution will be shown afterward.

#### 2.3 Visualiztion
If your problem was generated by the default parameters, you can run ui.py to visualizing the steps in the solution.






