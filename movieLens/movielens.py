# -*- coding: utf-8 -*-
"""movieLens.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1T3SWwtaTiessdKsuwAolGuksDqTpshAf
"""

from fastai.collab import *
from fastai.tabular import *

user,item,title = 'userId','movieId','title'

from google.colab import drive
drive.mount('/content/drive')

path_data = "/content/drive/My Drive/ml-100k/u.data"

ratings = pd.read_csv(path_data, delimiter='\t', header=None,
                      names=[user,item,'rating','timestamp'])
ratings.head()

path_item = "/content/drive/My Drive/ml-100k/u.item"

movies = pd.read_csv(path_item,  delimiter='|', encoding='latin-1', header=None,
                    names=[item, 'title', 'date', 'N', 'url', *[f'g{i}' for i in range(19)]])
movies.head()

len(ratings)

rating_movie = ratings.merge(movies[[item, title]])
rating_movie.head()

data = CollabDataBunch.from_df(rating_movie, seed=42, valid_pct=0.1, item_name=title)

data.show_batch()

y_range = [0,5.5]

learn = collab_learner(data, n_factors=40, y_range=y_range, wd=1e-1)

learn.lr_find()
learn.recorder.plot(skip_end=15)

learn.fit_one_cycle(5, 5e-3)

learn.save('dotprod')

"""<h2>Analysis</h2>"""

learn.load('dotprod');

learn.model

g = rating_movie.groupby(title)['rating'].count()
top_movies = g.sort_values(ascending=False).index.values[:1000]
top_movies[:10]

g

"""<h2>Bias</h2>"""

movie_bias = learn.bias(top_movies, is_item=True)
movie_bias.shape

mean_ratings = rating_movie.groupby(title)['rating'].mean()
movie_ratings = [(b, i, mean_ratings.loc[i]) for i,b in zip(top_movies,movie_bias)]

mean_ratings

item0 = lambda o:o[0]

sorted(movie_ratings, key=item0)[:15]

sorted(movie_ratings, key=lambda o: o[0], reverse=True)[:15]

"""<h2>Weights</h2>"""

movie_w = learn.weight(top_movies, is_item=True)
movie_w.shape

movie_pca = movie_w.pca(3)
movie_pca.shape

fac0,fac1,fac2 = movie_pca.t()
movie_comp = [(f, i) for f,i in zip(fac0, top_movies)]

sorted(movie_comp, key=itemgetter(0), reverse=True)[:10]

sorted(movie_comp, key=itemgetter(0))[:10]

movie_comp = [(f, i) for f,i in zip(fac1, top_movies)]

sorted(movie_comp, key=itemgetter(0), reverse=True)[:10]

sorted(movie_comp, key=itemgetter(0))[:10]

idxs = np.random.choice(len(top_movies), 50, replace=False)
idxs = list(range(50))
X = fac0[idxs]
Y = fac2[idxs]
plt.figure(figsize=(15,15))
plt.scatter(X, Y)
for i, x, y in zip(top_movies[idxs], X, Y):
    plt.text(x,y,i, color=np.random.rand(3)*0.7, fontsize=11)
plt.show()