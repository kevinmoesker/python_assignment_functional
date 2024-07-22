# technical-test-

Repo used for python technical test

Before coding, make sure that the tests run correctly on your env.


------

I redid the tech test challenge in functional way to show how it would look if it were closer to FSharp.

Basically we would choose to have functional composition over inheritance. 
So we would make a discriminated union for the vehicle, Car and Bike and with the 
calculate distance function pattern match based on the type.

It makes more sense to do this in FSharp than python as we have stronger patternmatching and type guarantees.
But still there are benefits to being able to compose I think especially when dealing with data transformation pipelines.

Based on preference one might choose not to raise Errors the normal way but wrap the errors in a Result type(in fsharp it's often called Railway oriented programming)

I tried to balance between going all out with types and functional programming and staying pythonic.



