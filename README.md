# Thesis

This project is focused on recommendation system where the system creates a matrix that keeps track on the score similarity of the user and the features in the dataset

In order to run the model please open the "model.ipnyb"

*Please note that this is a prototype and only display the vendors dataset this is not the final outcome of the model*


### Content-Based Filtering

Idea: Recommend items (venue/vendor/caterer) that are similar to the user’s preferences based on item attributes.

Example: If a user asks for “Photographer in Tayabas under ₱20,000, Standard package”, the system finds vendors with attributes closest to that query.

Features: Location, Service/Capacity, Package, Price, Rating, Dishes (for catering).

### Cosine Similarity

Why: Because it measures how close two vectors (user preference vs item features) are, regardless of scale.

Formula:

similarity
(
𝐴
,
𝐵
)
=
𝐴
⋅
𝐵
∣
∣
𝐴
∣
∣
×
∣
∣
𝐵
∣
∣
similarity(A,B)=
∣∣A∣∣×∣∣B∣∣
A⋅B
	​


Example: If user vector = [Budget=20k, Service=Photographer, Location=Tayabas] → we compute similarity against all vendors and rank the top matches.

The model is a hybrid model using filters like Content-Based Filtering and Consine Similarity
