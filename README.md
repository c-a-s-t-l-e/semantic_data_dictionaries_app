# Semantic Data Dictionary App
This is a web app that allows one to upload data dictionaries and see if there are columns that are possibly related based on meaning amongst them.

---

## How It Works

## 1. TF-IDF Vector Computation

### a. Example Documents:

An example set of documents (sentences):

D1: "The cat sat on the mat."

D2: "The dog sat on the log."

D3: "Cats and dogs are animals."

### b. Tokenization and Vocabulary:

First, tokenize the documents and create a vocabulary:

Vocabulary: ["and", "animals", "are", "cat", "cats", "dog", "dogs", "log", "mat", "on", "sat", "the"] 

(Note: usually converted to lowercase and can be further processed with stemming/lemmatization)

### c. Term Frequency (TF):

Calculate the TF for each word in each document. Now use the simple raw count for TF:

| Word    | D1 | D2 | D3 |
| :------ | :- | :- | :- |
| the     | 2  | 2  | 0  |
| cat     | 1  | 0  | 0  |
| cats    | 0  | 0  | 1  |
| sat     | 1  | 1  | 0  |
| on      | 1  | 1  | 0  |
| mat     | 1  | 0  | 0  |
| dog     | 0  | 1  | 0  |
| dogs    | 0  | 0  | 1  |
| log     | 0  | 1  | 0  |
| and     | 0  | 0  | 1  |
| animals | 0  | 0  | 1  |
| are     | 0  | 0  | 1  |

### d. Inverse Document Frequency (IDF):

Next, we calculate the IDF for each word in the vocabulary. Using the formula IDF(word) = log( (Total number of documents) / (Number of documents containing the word) ) + 1:

| Word    | IDF                             |
| :------ | :------------------------------ |
| the     | log(3/2) + 1 = 1.405            |
| cat     | log(3/1) + 1 = 2.099            |
| cats    | log(3/1) + 1 = 2.099            |
| sat     | log(3/2) + 1 = 1.405            |
| on      | log(3/2) + 1 = 1.405            |
| mat     | log(3/1) + 1 = 2.099            |
| dog     | log(3/1) + 1 = 2.099            |
| dogs    | log(3/1) + 1 = 2.099            |
| log     | log(3/1) + 1 = 2.099            |
| and     | log(3/1) + 1 = 2.099            |
| animals | log(3/1) + 1 = 2.099            |
| are     | log(3/1) + 1 = 2.099            |

### e. TF-IDF Calculation:

Now, we calculate the TF-IDF for each word in each document by multiplying TF and IDF:

| Word    | D1               | D2               | D3               |
| :------ | :--------------- | :--------------- | :--------------- |
| the     | 2 * 1.405 = 2.81 | 2 * 1.405 = 2.81 | 0 * 1.405 = 0    |
| cat     | 1 * 2.099 = 2.099 | 0                | 0                |
| cats    | 0                | 0                | 1 * 2.099 = 2.099 |
| sat     | 1 * 1.405 = 1.405 | 1 * 1.405 = 1.405 | 0                |
| on      | 1 * 1.405 = 1.405 | 1 * 1.405 = 1.405 | 0                |
| mat     | 1 * 2.099 = 2.099 | 0                | 0                |
| dog     | 0                | 1 * 2.099 = 2.099 | 0                |
| dogs    | 0                | 0                | 1 * 2.099 = 2.099 |
| log     | 0                | 1 * 2.099 = 2.099 | 0                |
| and     | 0                | 0                | 1 * 2.099 = 2.099 |
| animals | 0                | 0                | 1 * 2.099 = 2.099 |
| are     | 0                | 0                | 1 * 2.099 = 2.099 |

### f. Document Vectors:

Each document is now represented by a vector of TF-IDF scores:

D1: [2.81, 2.099, 0, 1.405, 1.405, 2.099, 0, 0, 0, 0, 0, 0]
D2: [2.81, 0, 0, 1.405, 1.405, 0, 2.099, 2.099, 2.099, 0, 0, 0]
D3: [0, 0, 2.099, 0, 0, 0, 0, 0, 0, 2.099, 2.099, 2.099]

### g. Storing Vectors in a Matrix

The document vectors are then stored as rows in a matrix, often called a document-term matrix or a TF-IDF matrix:


|      | the  | cat   | cats  | sat   | on   | mat   | dog   | dogs  | log   | and   | animals | are  |
|------|------|-------|-------|-------|------|-------|-------|-------|-------|-------|---------|------|
| D1  | 2.81 | 2.099 | 0     | 1.405 | 1.405| 2.099 | 0     | 0     | 0     | 0     | 0       | 0     |
| D2  | 2.81 | 0     | 0     | 1.405 | 1.405| 0     | 2.099 | 2.099 | 2.099 | 0     | 0       | 0     |
| D3  | 0     | 0     | 2.099 | 0     | 0     | 0     | 0     | 2.099 | 0     | 2.099 | 2.099   | 2.099 |

---

## 2. Cosine Similarity Computation

Compute the cosine similarity between D1 and D2 using their vectors:

D1: A = [2.81, 2.099, 0, 1.405, 1.405, 2.099, 0, 0, 0, 0, 0, 0]

D2: B = [2.81, 0, 0, 1.405, 1.405, 0, 2.099, 2.099, 2.099, 0, 0, 0]

### a. Dot Product (A · B):

The dot product is the sum of the products of corresponding elements:

A · B = (2.81 * 2.81) + (2.099 * 0) + (0 * 0) + (1.405 * 1.405) + (1.405 * 1.405) + (2.099 * 0) + (0 * 2.099) + (0 * 2.099) + (0 * 2.099) + (0 * 0) + (0 * 0) + (0 * 0)

A · B = 7.8961 + 0 + 0 + 1.974025 + 1.974025 + 0 + 0 + 0 + 0 + 0 + 0 + 0

A · B = 11.84415

### b. Magnitude (||A|| and ||B||):

The magnitude of a vector is the square root of the sum of the squares of its elements:

||A|| = sqrt(2.81^2 + 2.099^2 + 0^2 + 1.405^2 + 1.405^2 + 2.099^2 + 0^2 + 0^2 + 0^2 + 0^2 + 0^2 + 0^2)

||A|| = sqrt(7.8961 + 4.405801 + 0 + 1.974025 + 1.974025 + 4.405801 + 0 + 0 + 0 + 0 + 0 + 0 )

||A|| = sqrt(20.655752)

||A|| = 4.54486

||B|| = sqrt(2.81^2 + 0^2 + 0^2 + 1.405^2 + 1.405^2 + 0^2 + 2.099^2 + 2.099^2 + 2.099^2 + 0^2 + 0^2 + 0^2)

||B|| = sqrt(7.8961 + 0 + 0 + 1.974025 + 1.974025+ 0 + 4.405801+ 4.405801 + 4.405801+ 0 + 0 + 0)

||B|| = sqrt(25.061553)

||B|| = 5.006151

### c. Cosine Similarity:

Finally, we calculate the cosine similarity:

cosine_similarity(A, B) = (A · B) / (||A|| * ||B||)

cosine_similarity(A, B) = 11.84415 / (4.54486 * 5.006151)

cosine_similarity(A, B) = 11.84415 / 22.75198

cosine_similarity(A, B) = 0.5205
