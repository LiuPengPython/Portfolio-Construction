# 1_select_time.py：本模块获取由2016年7月1日到2018年12月31日的上证指数并把每个月月初第一个交易日的行情保存到000001M.csv，这一步需要手动确定所有月份中哪个月份涨幅最大，哪个月份跌幅最大。

from jqdatasdk import *
import time

auth(‘xxxx’, ‘xxxx’)

# 000001.XSHG	上证指数
# 000300.XSHG	沪深300
# 000905.XSHG	中证500
# 399005.XSHE	中小板指
# 399006.XSHE	创业板指


def down_trade_data(stock, start, end):
    df = get_price(stock, start_date=start, end_date=end, frequency='daily', fields=None, skip_paused=False, fq=None)
    df.to_csv('./select_time/' + stock[:-5] + '.csv')


def read_list():
    # filename是stock name list
    stocks = ['000001.XSHG']
    test_start = '2016-07-01'
    test_end = '2018-12-31'
    for i in range(len(stocks)):
        print(i)
        down_trade_data(stocks[i], test_start, test_end)
        print(get_query_count())
        time.sleep(0.1)


if __name__ == "__main__":
    read_list()
import pandas as pd


df = pd.read_csv('./select_time/000001.csv')


start = '6'
month_index = []
for i in range(df.shape[0]):
    if df.iloc[i, 0][6] != start:
        month_index.append(i)
        start = df.iloc[i, 0][6]
new_df = df.iloc[month_index, :]
new_df.to_csv('./select_time/000001M.csv')

# bull 20161101 20161130  0.048317982
# bear 20180601 20180630 -0.097419955

# 2_index_components.py：本模块根据第一个模块中确定的牛熊月份获取指定时间段中证500指数、中小板指和创业板指的成分股列表，共6个txt文件。

from jqdatasdk import *
import numpy as np
import time

auth(‘xxxx’, ‘xxxx’)

# 000001.XSHG	上证指数
# 000300.XSHG	沪深300
# 000905.XSHG	中证500
# 399005.XSHE	中小板指
# 399006.XSHE	创业板指


def down_trade_data(index_symbol, date, mode):
    ar = get_index_stocks(index_symbol, date=date)
    ar2save = []
    for stock in ar:
        ar2save.append(stock[:-5])
    np.savetxt('./stock_list/' + mode + ' ' + index_symbol[:-5] + '.txt', np.array(ar2save, dtype=np.str), delimiter='\n', fmt='%s')


def read_list():
    # filename是stock name list
    indexes = ['000905.XSHG', '399005.XSHE', '399006.XSHE']
    bull = '2016-11-01'
    bear = '2018-06-01'
    for i in range(len(indexes)):
        print(i)
        down_trade_data(indexes[i], bull, 'bull')
        print(get_query_count())
        time.sleep(0.1)
    for i in range(len(indexes)):
        print(i)
        down_trade_data(indexes[i], bear, 'bear')
        print(get_query_count())
        time.sleep(0.1)


if __name__ == "__main__":
    read_list()

# 3_cae_data.py：本模块根据模块1确定的时间和模块2确定的股票列表获取股票交易行情数据

import tushare as ts
import numpy as np
import time


def down_trade_data(stock, start, end, mode):
    pro = ts.pro_api ('xxxxxx')
    if stock[0] == '6':
        stock_code = stock + '.SH'
    else:
        stock_code = stock + '.SZ'
    df = pro.daily(ts_code=stock_code, start_date=start, end_date=end)
    if mode == 'train':
        df.to_csv('./cae_data/' + stock + '.csv')
    else:
        df.to_csv('./test_data/' + stock + '.csv')


def read_list(filename='stock_list.txt'):
    # filename是stock name list
    stocks = np.loadtxt(filename, dtype=np.str)
    train_start = '20161101'
    train_end = '20161130'
    test_start = '20161201'
    test_end = '20161231'
    for i in range(len(stocks)):
        print(i)
        down_trade_data(stocks[i], train_start, train_end, 'train')
        time.sleep(0.4)
        down_trade_data(stocks[i], test_start, test_end, 'test')
        time.sleep(0.4)


if __name__ == "__main__":
    read_list(filename='stock_list.txt')

# 4_mpl_finance.py：本模块是为了绘制蜡烛图而准备的函数库

import numpy as np
from matplotlib import colors as mcolors
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import TICKLEFT, TICKRIGHT, Line2D
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D
from six.moves import xrange, zip


def candlestick_ohlc(ax, quotes, width=0.2, colorup='k', colordown='r',
                     alpha=1.0):
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of (time, open, high, low, close, ...) sequences
        As long as the first 5 elements are these values,
        the record can be as long as you want (e.g., it may store volume).

        time must be in float days format - see date2num

    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """
    return _candlestick(ax, quotes, width=width, colorup=colorup,
                        colordown=colordown,
                        alpha=alpha, ochl=False)


def _candlestick(ax, quotes, width=0.2, colorup='k', colordown='r',
                 alpha=1.0, ochl=True):
    """
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown

    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of quote sequences
        data to plot.  time must be in float date format - see date2num
        (time, open, high, low, close, ...) vs
        (time, open, close, high, low, ...)
        set by `ochl`
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level
    ochl: bool
        argument to select between ochl and ohlc ordering of quotes

    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added

    """

    OFFSET = width / 2.0

    lines = []
    patches = []
    for q in quotes:
        if ochl:
            t, open, close, high, low = q[:5]
        else:
            t, open, high, low, close = q[:5]

        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - OFFSET, lower),
            width=width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)
    ax.autoscale_view()

    return lines, patches

# 5_draw.py：本模块绘制卷积神经网络所需训练数据

import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from mpl_finance import candlestick_ohlc
import datetime
import pandas as pd
import numpy as np


def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(str(date), '%Y%m%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time


def draw(stock):
    # dataframe转换为二维数组
    data = pd.read_csv('./cae_data/'+stock+'.csv')
    mat_data = data.values
    mat_data = mat_data[:, 2:]
    num_time = date_to_num(mat_data[:, 0])
    mat_data[:, 0] = num_time

    plt.rcParams['savefig.dpi'] = 100  # 图片像素
    fig, ax = plt.subplots(figsize=(3, 3))
    candlestick_ohlc(ax, mat_data, width=0.6, colorup='r', colordown='g', alpha=1.0)
    plt.grid(True)
    # 设置日期刻度旋转的角度
    plt.xticks(rotation=30)
    plt.xlabel('Date')
    plt.ylabel('Price')
    # x轴的刻度为日期
    ax.xaxis_date()
    plt.axis('off')
    plt.savefig('./candle/'+stock+'.jpg')


def read_list(filename='stock_list.txt'):
    stocks = np.loadtxt(filename, dtype=np.str)
    for i in range(len(stocks)):
        print(i)
        draw(stocks[i])


if __name__ == "__main__":
    read_list(filename='stock_list.txt')

# 6_draw_val.py：本模块绘制卷积神经网络所需验证数据

import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from mpl_finance import candlestick_ohlc
import datetime
import pandas as pd
import numpy as np


def date_to_num(dates):
    num_time = []
    for date in dates:
        date_time = datetime.datetime.strptime(str(date), '%Y%m%d')
        num_date = date2num(date_time)
        num_time.append(num_date)
    return num_time


def draw(stock):
    # dataframe转换为二维数组
    data = pd.read_csv('./test_data/'+stock+'.csv')
    mat_data = data.values
    mat_data = mat_data[:, 2:]
    num_time = date_to_num(mat_data[:, 0])
    mat_data[:, 0] = num_time

    plt.rcParams['savefig.dpi'] = 100  # 图片像素
    fig, ax = plt.subplots(figsize=(3, 3))
    candlestick_ohlc(ax, mat_data, width=0.6, colorup='r', colordown='g', alpha=1.0)
    plt.grid(True)
    # 设置日期刻度旋转的角度
    plt.xticks(rotation=30)
    plt.xlabel('Date')
    plt.ylabel('Price')
    # x轴的刻度为日期
    ax.xaxis_date()
    plt.axis('off')
    plt.savefig('./candle_val/'+stock+'.jpg')


def read_list(filename='stock_list.txt'):
    stocks = np.loadtxt(filename, dtype=np.str)
    for i in range(len(stocks)):
        print(i)
        draw(stocks[i])


if __name__ == "__main__":
    read_list(filename='stock_list.txt')

# 7_construct_new_list.py：通过观察绘制的图像，可以轻松得知哪些股票因为停盘而没有交易数据，本模块使用由手工构建的tingpai.txt，将原stock_list.txt中停盘的股票去除。

import numpy as np

stocks = np.loadtxt('stock_list.txt', dtype=np.str)
tingpai = np.loadtxt('tingpai.txt', dtype=np.str)
np.savetxt('stock_list.txt', np.array(list(set(stocks)-set(tingpai)), dtype=np.str), fmt='%s')

# 8_cae_with_loss_val.py：本模块使用以上模块绘制蜡烛图训练卷积神经网络自编码器并绘制训练损失图和最终效果图。

from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
import matplotlib.pyplot as plt
import numpy as np
import keras
from keras.utils import plot_model


class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch': [], 'epoch': []}
        self.val_loss = {'batch': [], 'epoch': []}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.val_loss['batch'].append(logs.get('val_loss'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.val_loss['epoch'].append(logs.get('val_loss'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))
        plt.figure()
        # loss
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':
            # val_loss
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)
        plt.xlabel(loss_type)
        plt.ylabel('loss')
        plt.legend(loc="upper right")
        plt.savefig('cae_loss.jpg')


input_img = Input(shape=(300, 300, 3))  # adapt this if using `channels_first` image data format

x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
encoded = MaxPooling2D((2, 2), padding='same')(x)

# at this point the representation is (38, 38, 8) i.e. 128-dimensional

x = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu')(x)
x = UpSampling2D((2, 2))(x)
decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)

autoencoder = Model(input_img, decoded)
plot_model(autoencoder, to_file='model_cae.jpg', show_shapes=True)
autoencoder.summary()
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

x_train = []
# 真实训练时这里需要读取股票名称列表然后去目录下读取图片
# TODO: 且将3份stock_list.txt，atten_data/labels.csv拼接起来
# TODO: candle，candle_val，atten_data复制到一起
stock_list = np.loadtxt('stock_list.txt', dtype=np.str)
for stock in stock_list:
    filename = './candle/'+str(stock)+'.jpg'
    image = np.array(plt.imread(filename))
    x_train.append(image)
x_train = np.array(x_train)
x_train = x_train.astype('float32') / 255.
x_train = np.reshape(x_train, (len(x_train), 300, 300, 3))

x_val = []
# 真实训练时这里需要读取股票名称列表然后去目录下读取图片
# TODO: 且将3份stock_list.txt，atten_data/labels.csv拼接起来
# TODO: candle，candle_val，atten_data复制到一起
stock_list = np.loadtxt('stock_list.txt', dtype=np.str)
for stock in stock_list:
    filename = './candle_val/'+str(stock)+'.jpg'
    image = np.array(plt.imread(filename))
    x_val.append(image)
x_val = np.array(x_val)
x_val = x_val.astype('float32') / 255.
x_val = np.reshape(x_val, (len(x_val), 300, 300, 3))

# 创建一个实例history
history = LossHistory()
# autoencoder.load_weights('cae.h5')
autoencoder.fit(x_train, x_train,
                epochs=10,
                batch_size=4,
                validation_data=(x_val[:100], x_val[:100]),
                shuffle=True,
                callbacks=[history])
autoencoder.save_weights('cae.h5')

# 绘制acc-loss曲线
history.loss_plot('epoch')


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


decoded_imgs = autoencoder.predict(x_train)
n = 5
plt.figure(figsize=(20, 10))
for i in range(n):
    # display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(rgb2gray(x_train[i].reshape(300, 300, 3)), cmap='gray')

    # display reconstruction
    ax = plt.subplot(2, n, i + n + 1)
    plt.imshow(rgb2gray(decoded_imgs[i].reshape(300, 300, 3)), cmap='gray')
plt.savefig('cae.jpg')

# 9_cae_extract.py：本模块利用训练好的卷积神经网络自编码器将蜡烛图提取为数字特征。

from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
import matplotlib.pyplot as plt
import numpy as np


input_img = Input(shape=(300, 300, 3))  # adapt this if using `channels_first` image data format

x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
encoded = MaxPooling2D((2, 2), padding='same')(x)

# at this point the representation is (38, 38, 8) i.e. 128-dimensional

x = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(32, (3, 3), activation='relu')(x)
x = UpSampling2D((2, 2))(x)
decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.summary()
autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

autoencoder.load_weights('cae.h5')
encoder = Model(inputs=autoencoder.input, outputs=autoencoder.get_layer('max_pooling2d_4').output)

# 真实训练时这里需要读取股票名称列表然后去目录下读取图片
stock_list = np.loadtxt('stock_list.txt', dtype=np.str)
with open('encoded_vecs.csv', 'w') as f_obj:
    pass
for stock in stock_list:
    filename = './candle/'+str(stock)+'.jpg'
    image = np.array(plt.imread(filename))
    x_train = image.astype('float32') / 255.
    x_train = np.reshape(x_train, (1, 300, 300, 3))
    encoded_vec = encoder.predict(x_train)
    # print(encoded_vec.shape)
    encoded_vec = encoded_vec.ravel()
    # print(encoded_vec.shape)
    with open('encoded_vecs.csv', 'a') as f_obj:
        f_obj.write(str(stock))
        f_obj.write(',')
        f_obj.write(','.join(map(str, encoded_vec)))
        f_obj.write('\n')

# 10_pca_graph.py：本模块将上一模块提取的特征进行PCA降维。

import pandas as pd
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

data = pd.read_csv('encoded_vecs.csv', header=None, index_col=0)
row_std = data.std(axis=0)
# plt.hist(row_std)
bar = row_std.quantile(q=0.80)
print('bar')
print(bar)
mask = []
for i in range(len(row_std)):
    if row_std.iloc[i] > bar:
        mask.append(i)
data = data.iloc[:, mask]

pca = PCA(n_components=2)
pca.fit(data)
print('explained_variance_ratio')
print(sum(pca.explained_variance_ratio_))
X_new = pca.transform(data)
# fig = plt.figure()
# ax = Axes3D(fig, rect=[0, 0, 1, 1], elev=30, azim=20)
# plt.scatter(X_new[:, 0], X_new[:, 1], X_new[:, 2], marker='$1$')
# plt.scatter(X_new[:, 0], X_new[:, 1], marker='$1$')

code2indu = {}
with open('indus.txt', 'r') as f_obj:
    for i in f_obj.readlines():
        line = i.strip().split()
        print()
        code2indu[line[0]] = line[1]
indu2num = {}
with open('num.txt', 'r') as f_obj:
    for i in f_obj.readlines():
        line = i.strip().split()
        print()
        indu2num[line[0]] = line[1]
color_map = {
    0:'red',
    1:'orange',
    2:'yellow',
    3:'green',
    4:'cyan',
    5:'blue',
    6:'purple',
    7:'saddlebrown',
    8:'black',
    9:'gray'
}
stocks = np.loadtxt('stock_list.txt', dtype=np.str)
fig = plt.figure()
ax1 = fig.add_subplot(111)
for i in range(len(stocks)):
    ax1.scatter(X_new[i, 0], X_new[i, 1], c=color_map[int(indu2num[code2indu[stocks[i]]])], marker='$'+indu2num[code2indu[stocks[i]]]+'$')
plt.savefig('pca_graph.jpg')


def save(n, data):
    pca = PCA(n_components=n)
    pca.fit(data)
    print('explained_variance_ratio')
    print(sum(pca.explained_variance_ratio_))
    np.savetxt('extracted_features.csv', pca.transform(data), delimiter=',')


if __name__ == "__main__":
    save(40, data)

# 11_cluster.py：本模块根据降维后的数据将股票进行聚类，可选聚类方法包括MeanShift、DBSCAN和高斯混合模型

# import numpy as np
# from sklearn.cluster import MeanShift, estimate_bandwidth
# import matplotlib.pyplot as plt
# from itertools import cycle
#
# X = np.loadtxt('extracted_features.csv', delimiter=',')
# bandwidth = estimate_bandwidth(X, quantile=0.5)
# ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
# ms.fit(X)
#
# labels = ms.labels_
# np.savetxt('cluster_labels.csv', labels, delimiter='\n')
# cluster_centers = ms.cluster_centers_
# labels_unique = np.unique(labels)
# n_clusters_ = len(labels_unique)
# print("number of estimated clusters: %d" % n_clusters_)
#
# plt.figure(1)
# plt.clf()
# colors = cycle('bgrcmyk')
# for k, col in zip(range(n_clusters_), colors):
#     my_members = labels == k
#     cluster_center = cluster_centers[k]
#     plt.plot(X[my_members, 0], X[my_members, 1], col + '.')
#     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
# plt.title("Estimated number of clusters: %d" % n_clusters_)
# plt.show()


# eps默认是0.5，过大，此时我们的类别数可能会减少，反之则类别数可能会增大
# min_samples默认值是5. 在eps一定的情况下，min_samples过大，类别数也会变多。反之min_samples过小，可能会导致类别数过少
# from sklearn.cluster import DBSCAN
# import numpy as np
# import matplotlib.pyplot as plt
#
# plt.clf()
# X = np.loadtxt('extracted_features.csv', delimiter=',')
# y_pred = DBSCAN(eps=0.1, min_samples=10).fit_predict(X)
# np.savetxt('cluster_labels.csv', y_pred, delimiter='\n')
# plt.scatter(X[:, 0], X[:, 1], c=y_pred)
# plt.show()

# TODO:自动分类效果不好就上kmeans或者gmm强制分成k组
from sklearn.mixture import GMM
import numpy as np
import matplotlib.pyplot as plt

plt.clf()
X = np.loadtxt('extracted_features.csv', delimiter=',')
gmm = GMM(n_components=4).fit(X)
y_pred = gmm.predict(X)
np.savetxt('cluster_labels.csv', y_pred, delimiter='\n', fmt='%d')
plt.scatter(X[:, 0], X[:, 1], c=y_pred, cmap='Set1')
plt.show()

# 12_attn_data.py：本模块获取注意力机制训练数据。

from jqdatasdk import *
import numpy as np
import pandas as pd
import time

auth(‘xxxx’, ‘xxxx’)


def down_trade_data(stock, start, end):
    if stock[0] == '6':
        stock_code = stock + '.XSHG'
    else:
        stock_code = stock + '.XSHE'
    df = get_money_flow(stock_code, start_date=start, end_date=end)
    for i in range(df.shape[0]):
        df.iloc[i, 0] = int(df.iloc[i, 0].strftime('%Y%m%d'))
    # 获取jq数据后读取cae_data，然后merge
    ts_data = pd.read_csv('./cae_data/'+stock+'.csv', index_col=0).loc[:, ['trade_date', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']]
    df2save = pd.merge(ts_data, df, left_on='trade_date', right_on='date', how='left')
    df2save.to_csv('./atten_data/' + stock + '.csv')


def build_labels(filename='stock_list.txt'):
    # TODO: 这个可能得改，一个月大概都会涨，缩短时间
    stocks = np.loadtxt(filename, dtype=np.str)
    labels = []
    for stock in stocks:
        test_data = pd.read_csv('./test_data/'+stock+'.csv', index_col=0)
        if test_data.iloc[0, 5] - test_data.iloc[-1, 5] > 0:
            labels.append(1)
        else:
            labels.append(0)
    np.savetxt('./atten_data/labels.csv', np.array(labels), delimiter='\n', fmt='%d')


def read_list(filename='stock_list.txt'):
    # filename是stock name list
    stocks = np.loadtxt(filename, dtype=np.str)
    train_start = '2016-11-01'
    train_end = '2016-11-30'
    for i in range(len(stocks)):
        print(i)
        down_trade_data(stocks[i], train_start, train_end)
        print(get_query_count())
        time.sleep(0.1)


if __name__ == "__main__":
    read_list(filename='stock_list.txt')
    build_labels(filename='stock_list.txt')

# 13_self_attn.py：本模块训练注意力机制模型。

from keras import backend as K
from keras.engine.topology import Layer
from keras.models import Model
from keras.layers import *
import pandas as pd
import numpy as np


maxlen = 23
batch_size = 4

# TODO: 将3份stock_list和labels拼接起来
x_train = []
stock_list = np.loadtxt('stock_list.txt', dtype=np.str)
for stock in stock_list:
    filename = './atten_data/'+str(stock)+'.csv'
    df = pd.read_csv(filename, index_col=0)
    df.drop(['trade_date', 'date', 'sec_code'], axis=1, inplace=True)
    new_df = (df - df.mean()) / df.std()
    x_train.append(new_df)
# pad 后尺寸为(m, 23, -1)
pad_x_train = np.zeros((len(x_train), 23, 16))
for i in range(len(x_train)):
    pad_x_train[i, :x_train[i].shape[0], :] = x_train[i]

y_train = np.loadtxt('./atten_data/labels.csv')


class Position_Embedding(Layer):

    def __init__(self, size=None, mode='sum', **kwargs):
        self.size = size  # 必须为偶数
        self.mode = mode
        super(Position_Embedding, self).__init__(**kwargs)

    def call(self, x):
        if (self.size == None) or (self.mode == 'sum'):
            self.size = int(x.shape[-1])
        batch_size, seq_len = K.shape(x)[0], K.shape(x)[1]
        position_j = 1. / K.pow(10000., \
                                2 * K.arange(self.size / 2, dtype='float32' \
                                             ) / self.size)
        position_j = K.expand_dims(position_j, 0)
        position_i = K.cumsum(K.ones_like(x[:, :, 0]), 1) - 1  # K.arange不支持变长，只好用这种方法生成
        position_i = K.expand_dims(position_i, 2)
        position_ij = K.dot(position_i, position_j)
        position_ij = K.concatenate([K.cos(position_ij), K.sin(position_ij)], 2)
        if self.mode == 'sum':
            return position_ij + x
        elif self.mode == 'concat':
            return K.concatenate([position_ij, x], 2)

    def compute_output_shape(self, input_shape):
        if self.mode == 'sum':
            return input_shape
        elif self.mode == 'concat':
            return (input_shape[0], input_shape[1], input_shape[2] + self.size)


class Attention(Layer):

    def __init__(self, nb_head, size_per_head, **kwargs):
        self.nb_head = nb_head
        self.size_per_head = size_per_head
        self.output_dim = nb_head * size_per_head
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.WQ = self.add_weight(name='WQ',
                                  shape=(input_shape[0][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.WK = self.add_weight(name='WK',
                                  shape=(input_shape[1][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.WV = self.add_weight(name='WV',
                                  shape=(input_shape[2][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        super(Attention, self).build(input_shape)

    def Mask(self, inputs, seq_len, mode='mul'):
        if seq_len == None:
            return inputs
        else:
            mask = K.one_hot(seq_len[:, 0], K.shape(inputs)[1])
            mask = 1 - K.cumsum(mask, 1)
            for _ in range(len(inputs.shape) - 2):
                mask = K.expand_dims(mask, 2)
            if mode == 'mul':
                return inputs * mask
            if mode == 'add':
                return inputs - (1 - mask) * 1e12

    def call(self, x):
        # 如果只传入Q_seq,K_seq,V_seq，那么就不做Mask
        # 如果同时传入Q_seq,K_seq,V_seq,Q_len,V_len，那么对多余部分做Mask
        if len(x) == 3:
            Q_seq, K_seq, V_seq = x
            Q_len, V_len = None, None
        elif len(x) == 5:
            Q_seq, K_seq, V_seq, Q_len, V_len = x
        # 对Q、K、V做线性变换
        Q_seq = K.dot(Q_seq, self.WQ)
        Q_seq = K.reshape(Q_seq, (-1, K.shape(Q_seq)[1], self.nb_head, self.size_per_head))
        Q_seq = K.permute_dimensions(Q_seq, (0, 2, 1, 3))
        K_seq = K.dot(K_seq, self.WK)
        K_seq = K.reshape(K_seq, (-1, K.shape(K_seq)[1], self.nb_head, self.size_per_head))
        K_seq = K.permute_dimensions(K_seq, (0, 2, 1, 3))
        V_seq = K.dot(V_seq, self.WV)
        V_seq = K.reshape(V_seq, (-1, K.shape(V_seq)[1], self.nb_head, self.size_per_head))
        V_seq = K.permute_dimensions(V_seq, (0, 2, 1, 3))
        # 计算内积，然后mask，然后softmax
        A = K.batch_dot(Q_seq, K_seq, axes=[3, 3]) / self.size_per_head ** 0.5
        A = K.permute_dimensions(A, (0, 3, 2, 1))
        A = self.Mask(A, V_len, 'add')
        A = K.permute_dimensions(A, (0, 3, 2, 1))
        A = K.softmax(A)
        # 输出并mask
        O_seq = K.batch_dot(A, V_seq, axes=[3, 2])
        O_seq = K.permute_dimensions(O_seq, (0, 2, 1, 3))
        O_seq = K.reshape(O_seq, (-1, K.shape(O_seq)[1], self.output_dim))
        O_seq = self.Mask(O_seq, Q_len, 'mul')
        return O_seq

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], input_shape[0][1], self.output_dim)


S_inputs = Input(shape=(23, 16))
O_seq = Attention(8, 16)([S_inputs, S_inputs, S_inputs])
O_seq = GlobalAveragePooling1D()(O_seq)
O_seq = Dropout(0.5)(O_seq)
outputs = Dense(1, activation='sigmoid')(O_seq)

model = Model(inputs=S_inputs, outputs=outputs)
# try using different optimizers and different optimizer configs
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

print('Train...')
model.fit(pad_x_train, y_train,
          batch_size=batch_size,
          epochs=50)
model.save_weights('attn.h5')

# 14_suggets.py：本模块根据聚类结果和训练好的注意力机制模型进行投资组合构建。

from keras import backend as K
from keras.engine.topology import Layer
from keras.models import Model
from keras.layers import *
import pandas as pd
import numpy as np
import operator


class Attention(Layer):

    def __init__(self, nb_head, size_per_head, **kwargs):
        self.nb_head = nb_head
        self.size_per_head = size_per_head
        self.output_dim = nb_head * size_per_head
        super(Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        self.WQ = self.add_weight(name='WQ',
                                  shape=(input_shape[0][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.WK = self.add_weight(name='WK',
                                  shape=(input_shape[1][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.WV = self.add_weight(name='WV',
                                  shape=(input_shape[2][-1], self.output_dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        super(Attention, self).build(input_shape)

    def Mask(self, inputs, seq_len, mode='mul'):
        if seq_len == None:
            return inputs
        else:
            mask = K.one_hot(seq_len[:, 0], K.shape(inputs)[1])
            mask = 1 - K.cumsum(mask, 1)
            for _ in range(len(inputs.shape) - 2):
                mask = K.expand_dims(mask, 2)
            if mode == 'mul':
                return inputs * mask
            if mode == 'add':
                return inputs - (1 - mask) * 1e12

    def call(self, x):
        # 如果只传入Q_seq,K_seq,V_seq，那么就不做Mask
        # 如果同时传入Q_seq,K_seq,V_seq,Q_len,V_len，那么对多余部分做Mask
        if len(x) == 3:
            Q_seq, K_seq, V_seq = x
            Q_len, V_len = None, None
        elif len(x) == 5:
            Q_seq, K_seq, V_seq, Q_len, V_len = x
        # 对Q、K、V做线性变换
        Q_seq = K.dot(Q_seq, self.WQ)
        Q_seq = K.reshape(Q_seq, (-1, K.shape(Q_seq)[1], self.nb_head, self.size_per_head))
        Q_seq = K.permute_dimensions(Q_seq, (0, 2, 1, 3))
        K_seq = K.dot(K_seq, self.WK)
        K_seq = K.reshape(K_seq, (-1, K.shape(K_seq)[1], self.nb_head, self.size_per_head))
        K_seq = K.permute_dimensions(K_seq, (0, 2, 1, 3))
        V_seq = K.dot(V_seq, self.WV)
        V_seq = K.reshape(V_seq, (-1, K.shape(V_seq)[1], self.nb_head, self.size_per_head))
        V_seq = K.permute_dimensions(V_seq, (0, 2, 1, 3))
        # 计算内积，然后mask，然后softmax
        A = K.batch_dot(Q_seq, K_seq, axes=[3, 3]) / self.size_per_head ** 0.5
        A = K.permute_dimensions(A, (0, 3, 2, 1))
        A = self.Mask(A, V_len, 'add')
        A = K.permute_dimensions(A, (0, 3, 2, 1))
        A = K.softmax(A)
        # 输出并mask
        O_seq = K.batch_dot(A, V_seq, axes=[3, 2])
        O_seq = K.permute_dimensions(O_seq, (0, 2, 1, 3))
        O_seq = K.reshape(O_seq, (-1, K.shape(O_seq)[1], self.output_dim))
        O_seq = self.Mask(O_seq, Q_len, 'mul')
        return O_seq

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], input_shape[0][1], self.output_dim)


S_inputs = Input(shape=(23, 16))
O_seq = Attention(8,16)([S_inputs, S_inputs, S_inputs])
O_seq = GlobalAveragePooling1D()(O_seq)
O_seq = Dropout(0.5)(O_seq)
outputs = Dense(1, activation='sigmoid')(O_seq)

model = Model(inputs=S_inputs, outputs=outputs)
# try using different optimizers and different optimizer configs
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.load_weights('attn.h5')


labels = pd.read_csv('cluster_labels.csv', header=None, dtype=np.str)
unique_labels = np.unique(labels)
portfolio = []
for l in unique_labels:
    attn_pred = {}
    # 把stocklist和labels,pd.concat(,axis=1)
    stocklist = pd.read_csv('stock_list.txt', header=None, dtype=np.str)
    clusters = pd.concat([stocklist, labels], axis=1)
    clusters.columns = ['stock', 'label']
    for stock in clusters[clusters.label == l].iloc[:, 0]:
        filename = './atten_data/' + str(stock) + '.csv'
        df = pd.read_csv(filename, index_col=0)
        df.drop(['trade_date', 'date', 'sec_code'], axis=1, inplace=True)
        new_df = (df - df.mean()) / df.std()
        x_train = new_df
        # pad 后 x_train = np.array(pad).reshape((1, 23, -1))
        pad = np.zeros((1, 23, 16))
        pad[0, :x_train.shape[0], :] = x_train
        attn_pred[stock] = float(model.predict(pad))
    # 按照value排序，返回第一个的key
    d = sorted(attn_pred.items(), key=operator.itemgetter(1), reverse=True)
    key = d[0][0]
    portfolio.append(key)

np.savetxt('portfolio.txt', np.array(portfolio, dtype=np.str), delimiter='\n', fmt='%s')

# 15_index_data.py：本模块获取用与对比的指数数据。

from jqdatasdk import *
import time

auth(‘xxxx’, ‘xxxx’)

# 000001.XSHG	上证指数
# 000300.XSHG	沪深300
# 000905.XSHG	中证500
# 399005.XSHE	中小板指
# 399006.XSHE	创业板指


def down_trade_data(stock, start, end):
    df = get_price(stock, start_date=start, end_date=end, frequency='daily', fields=None, skip_paused=False, fq=None)
    df.to_csv('./test_data/' + stock[:-5] + '.csv')


def read_list():
    # filename是stock name list
    stocks = ['000001.XSHG', '000300.XSHG', '000905.XSHG', '399005.XSHE', '399006.XSHE']
    test_start = '2016-12-01'
    test_end = '2016-12-31'
    for i in range(len(stocks)):
        print(i)
        down_trade_data(stocks[i], test_start, test_end)
        print(get_query_count())
        time.sleep(0.1)


if __name__ == "__main__":
    read_list()

# 16_fund_data.py：本模块获取用于对比的基金数据。

from jqdatasdk import *
from datetime import datetime
import time

auth(‘xxxx’, ‘xxxx’)

# http://fund.eastmoney.com/data/diyfundranking.html#tgp;c0;r;sqjzf;pn50;ddesc;qsd20170101;qed20170131;qdii


def down_trade_data(code, start, end):
    df = finance.run_query(query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == str(code),
                                                                finance.FUND_NET_VALUE.day > start,
                                                                finance.FUND_NET_VALUE.day < end).limit(30))
    df.to_csv('./test_data/' + str(code) + '.csv')


def read_list():
    # filename是stock name list
    # http://fund.eastmoney.com/data/diyfundranking.html#tgp;c0;r;sqjzf;pn50;ddesc;qsd20170101;qed20170131;qdii
    # 通过上网址获取选取月份下月的收益最高的基金code
    main_codes = ['003475', '000326', '161725', '519606', '003190']
    test_start = datetime(2016, 11, 30, 0, 0)
    test_end = datetime(2017, 1, 1, 0, 0)
    for i in range(len(main_codes)):
        print(i)
        down_trade_data(main_codes[i], test_start, test_end)
        print(get_query_count())
        time.sleep(0.1)


if __name__ == "__main__":
    read_list()

# 17_compare.py：本模块用于生成对比结果Excel表。

import numpy as np
import pandas as pd


portfolio_stock = np.loadtxt('portfolio.txt', dtype=np.str)
portfolio_performance = pd.read_csv('./test_data/'+portfolio_stock[0]+'.csv', index_col=0)
for stock in portfolio_stock[1:]:
    portfolio_performance += pd.read_csv('./test_data/' + stock + '.csv', index_col=0)
# portfolio_performance reverse 变成时间正序
portfolio_performance.iloc[::-1].to_csv('./test_data/portfolio.csv')

rf = 0.0315 / 360

compare_list = ['portfolio', '000001', '000300', '000905', '399005', '399006']
result = np.zeros((6, 7))
result = pd.DataFrame(result)
code2name = {'portfolio':'投资组合', '000001':'上证指数', '000300':'沪深300', '000905':'中证500', '399005':'中小板指', '399006':'创业板指'}
for row in range(6):
    cur_data = pd.read_csv('./test_data/'+compare_list[row]+'.csv').loc[:, 'close']
    cur_data = np.array(cur_data)
    result.iloc[row, 0] = code2name[compare_list[row]]
    result.iloc[row, 1] = (cur_data[-1] - cur_data[0]) / cur_data[0]
    average_return = (cur_data[1:] - cur_data[:-1]) / cur_data[:-1]
    result.iloc[row, 2] = np.mean(average_return)
    result.iloc[row, 3] = np.std(average_return)
    result.iloc[row, 4] = (result.iloc[row, 2] - rf) / result.iloc[row, 3]
    result.iloc[row, 5] = (np.max(cur_data) - np.min(cur_data)) / np.max(cur_data)
    result.iloc[row, 6] = np.sum(average_return>0)
result.columns = ['种类', '月收益', '日收益均值', '日收益标准差', '夏普比率', '最大回撤比率', '盈利天数']
result.to_csv('index_compare_result.csv')


compare_list = ['portfolio', '003475', '000326', '161725', '519606', '003190']
name_list = ['前海联合沪深30', '南方中小盘成长股', '招商中证白酒指数', '国泰金鑫', '创金合信消费主题']
result = np.zeros((6, 7))
result = pd.DataFrame(result)
code2name = {'portfolio': '投资组合'}
for i in range(5):
    code2name[compare_list[i+1]] = name_list[i]
for row in range(6):
    if row == 0:
        cur_data = pd.read_csv('./test_data/'+compare_list[row]+'.csv').loc[:, 'close']
        cur_data = np.array(cur_data)
        result.iloc[row, 0] = code2name[compare_list[row]]
        result.iloc[row, 1] = (cur_data[-1] - cur_data[0]) / cur_data[0]
        average_return = (cur_data[1:] - cur_data[:-1]) / cur_data[:-1]
        result.iloc[row, 2] = np.mean(average_return)
        result.iloc[row, 3] = np.std(average_return)
        result.iloc[row, 4] = (result.iloc[row, 2] - rf) / result.iloc[row, 3]
        result.iloc[row, 5] = (np.max(cur_data) - np.min(cur_data)) / np.max(cur_data)
        result.iloc[row, 6] = np.sum(average_return > 0)
    else:
        cur_data = pd.read_csv('./test_data/' + compare_list[row] + '.csv').loc[:, 'net_value']
        cur_data = np.array(cur_data)
        result.iloc[row, 0] = code2name[compare_list[row]]
        result.iloc[row, 1] = (cur_data[-1] - cur_data[0]) / cur_data[0]
        average_return = (cur_data[1:] - cur_data[:-1]) / cur_data[:-1]
        result.iloc[row, 2] = np.mean(average_return)
        result.iloc[row, 3] = np.std(average_return)
        result.iloc[row, 4] = (result.iloc[row, 2] - rf) / result.iloc[row, 3]
        result.iloc[row, 5] = (np.max(cur_data) - np.min(cur_data)) / np.max(cur_data)
        result.iloc[row, 6] = np.sum(average_return > 0)
result.columns = ['种类', '月收益', '日收益均值', '日收益标准差', '夏普比率', '最大回撤比率', '盈利天数']
result.to_csv('fund_compare_result.csv')
