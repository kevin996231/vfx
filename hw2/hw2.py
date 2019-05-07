import numpy as np
from scipy.ndimage import filters 
import cv2
import matplotlib.pyplot as plt 
import math
import random
def harris(image, sigma, k): #input k for change the value easily
	# derivatives
	image_x = np.zeros(image.shape)
	image_y = np.zeros(image.shape)
	# compute components of the Harris matrix
	# image_x, image_y = np.gradient(image)
	filters.gaussian_filter(image, (sigma, sigma), (0, 1), image_x)
	filters.gaussian_filter(image, (sigma, sigma), (1, 0), image_y)
	xx = image_x * image_x
	xy = image_x * image_y
	yy = image_y * image_y
	Ixx = filters.gaussian_filter(xx, sigma)
	Ixy = filters.gaussian_filter(xy, sigma)
	Iyy = filters.gaussian_filter(yy, sigma)
	# 指 {\displaystyle \mathbf {A} } \mathbf{A}的主對角線（從左上方至右下方的對角線）上各個元素的總和
	delta = Ixx * Iyy - Ixy * Ixy
	trace = Ixx + Iyy +1e-10
	# R = detM - k(trace(M)^2)
	# 0.04 < k < 0.06
	R = delta - k*(trace**2)
	# R = delta/trace
	return R
def supression(R,win=7):
	R[  :win ,  :] = 0
	R[-win:  ,  :] = 0
	R[  :  ,  :win] = 0
	R[  :  ,-win:] = 0
	# median  = np.median(R)
	# print(median)
	# print(np.max(R))
	# print(np.min(R))
	# print(R)
	minimum = np.min(R)
	print(minimum)
	h = R.shape[0]
	w = R.shape[1]
	print(h,w)
	x = []
	y = []
	maximum = []
	for i in range(500):
		max = np.argmax(R)
		maximum.append(max)
		maxh = max//w
		maxw = max%w
		y.append(maxh)
		x.append(maxw)
		R[maxh-win:maxh+win+1,maxw-win:maxw+win+1] = minimum
	return (x,y)
 
# plot corner
def plot_corners(img,path, coor_x, coor_y): 
	# fig = figure(figsize=(15, 8))
	plt.imshow(img, cmap = 'gray')
	plt.plot(coor_x, coor_y, 'r*', markersize=1)
	plt.axis('off')
	plt.savefig(path)
	plt.show()
	plt.clf()

# feature description : 將圖片獨特之處寫成數值，以供辨識比對
# (SIFT) ：
# 一個像素進行投票，梯度長度是持票數，梯度角度決定投票箱編號。 360° 等分成 8 個箱子。一個像素投票給一個箱子。
# By assigning a consistent orientation, the keypoint descriptor can be orientation invariant.
# def orientation(Ix, Iy, bins, kernel_size):
# 	m = np.sqrt(Ix**2 + Iy**2)
# 	# 0 ~ 2pi
# 	theta = np.arctan(Iy/ (Ix+1e-8))*(180 / np.pi)
# 	theta[Ix < 0] += 180
# 	theta = (theta + 360) % 360
# 	# 4*4+8bin的descirptor是最好的，因此每个关键点将会产生128维的特征向量。
# 	binsize = 360. / bins
# 	theta_bin = (theta + binsize / 2) // int(binsize) % bins
# 	print(theta)
# 	print("binsize = ", binsize)
# 	print("theta_bin = ", theta_bin)
# Simplest solution :
def description(image, coor_x, coor_y, win):
	descriptor = np.zeros((500,(2*win+1)*(2*win+1)))
	for i in range(500):
		x = int(coor_x[i])
		y = int(coor_y[i])
		one_dim = image[y-win:y+win+1, x-win:x+win+1].flatten()
		descriptor[i] = one_dim
	return descriptor

def matching(des0,des1,coords_x0,coords_y0,coords_x1,coords_y1):
	used = np.zeros(500)
	new_coords_x0 = []
	new_coords_x1 = []
	new_coords_y0 = []
	new_coords_y1 = []
	for i in range(500):
		entropy = np.abs(des1 - des0[i])
		entropy = np.sum(entropy,axis = 1)

		index = np.argmin(entropy)
		min1 = np.min(entropy)
		entropy[index] = 100000000
		min2 = np.min(entropy)
		if min1 < min2 *0.7 :
			if used[index] == 0:
				used[index] = 1
				new_coords_x0.append(coords_x0[i])
				new_coords_x1.append(coords_x1[index])
				new_coords_y0.append(coords_y0[i])
				new_coords_y1.append(coords_y1[index])
	return new_coords_x0,new_coords_y0,new_coords_x1,new_coords_y1

def appendimages(image0, image1): #the appended images displayed side by side for image mapping
    
    # select the image with the fewest rows and fill in enough empty rows
    rows1 = image0.shape[0]
    rows2 = image1.shape[0]
    
    return np.concatenate((image0, image1), axis=1)

def plot_matching(image0, image1, new_coords_x0, new_coords_y0, new_coords_x1, new_coords_y1,path):
	plt.figure(figsize=(30, 20))
	image2 = appendimages(image0, image1)
	plt.imshow(image2, cmap = 'gray')
	for i in range(len(new_coords_x0)):
		# print(new_coords_x0[i], new_coords_y0[i])
		# print(new_coords_x1[i], new_coords_y1[i])
		# plt.plot([new_coords_x0[i], new_coords_y0[i]], [0,0], 'c', c=[np.random.random(), np.random.random(), np.random.random()])

		# plot([x[0], y[0]+cols1], [x[1], y[1]], 'r*', =[np.random.random(), np.random.random(), np.random.random()])
		plt.plot([new_coords_x0[i], new_coords_x1[i]+3264], [new_coords_y0[i], new_coords_y1[i]], 'c', c=[np.random.random(), np.random.random(), np.random.random()])
	# plt.show()
	plt.axis('off')
	plt.savefig(path)
	plt.clf()

#image_stitching
# RANSAC : find the best shift for the pair of pictures
def RANSAC(new_coords_x0,new_coords_y0, new_coords_x1, new_coords_y1, last_shift_x, last_shift_y, threshold, n=100):
	max_inlier = 0
	pairs_diff_x = []
	pairs_diff_y = []
	pairs_diff = np.zeros((2, len(new_coords_y0)))
	# calculate all [y0-x0, y1-x1]
	print(len(new_coords_x0))
	for k in range(len(new_coords_x0)):
		pairs_diff_x.append(new_coords_x0[k] - new_coords_x1[k])
		pairs_diff_y.append(new_coords_y0[k] - new_coords_y1[k])
	pairs_diff = np.array([pairs_diff_x, pairs_diff_y])
	pairs_diff[0] += last_shift_x
	pairs_diff[1] += last_shift_y
	diff = np.copy(pairs_diff)
	print(pairs_diff.shape)
	print(pairs_diff)
	# print(pairs_diff[:,74])
	max_inlier = 0
	for i in range(92):
		# print("i = ", i)
		random.seed()
		index = random.randint(0, len(new_coords_x0)-1)
		# print(pairs_diff)
		# print("index = ", index)
		shift = pairs_diff[:,index]
		# print("shift = ", shift)
		diff[0] = pairs_diff[0] - shift[0]
		diff[1] = pairs_diff[1] - shift[1]
		inlier = 0
		for j in range(diff.shape[1]):
			dis = diff[: , j]
			if dis[0] ** 2 + dis[1] ** 2 < threshold:
				inlier += 1
		if inlier > max_inlier:
			max_inlier = inlier
			best_shift = shift
			# drift
	return best_shift
def blending(img0, img1, best_shift,pre_h):
	# img0.shape <512,384>
	# best_shift[0] = x
	# best_shift[1] = y
	img0_h, img0_w, _ = img0.shape
	img1_h, img1_w, _ = img1.shape

	best_shift[0] = img1_w - abs(best_shift[0])
	# best_shift[1] = img0_h - abs(best_shift[1])
	matched_h = int(max(img0_h ,img1_h) + abs(best_shift[1]))
	matched_w = int(img0_w + img1_w - abs(best_shift[0]))
	print("best_shift = ", best_shift)
	print("matched_w = ", matched_w)
	print("matched_h = ", matched_h)

	new_img0 = np.zeros((matched_h, matched_w,3))
	new_img1 = np.zeros((matched_h, matched_w,3))

	h = pre_h + best_shift[1]
# h = now pic x value before merge
# hh = now pic x value after merge
	if h < 0:
		hh = 0
	else:
		hh = h
	if h >= 0:
		new_img0[0:img0_h, 0:img0_w,:] = img0
		# new_img1[matched_h-img1_h:matched_h, matched_w-img1_w:matched_w] = img1
		new_img1[hh:hh+img1_h, matched_w-img1_w:matched_w,:] = img1

	else:
		# new_img0[matched_h-img0_h:matched_h, 0:img0_w] = img0
		new_img0[-h:-h+img0_h, 0:img0_w,:] = img0

		# new_img1[0:img1_h, matched_w-img1_w:matched_w] = img1
		new_img1[0:img1_h, matched_w-img1_w:matched_w,:] = img1


	# cv2.imwrite("new_img0", new_img0)
	# cv2.imwrite("new_img1", new_img1)
	#blending(alpha)
	blending_img = np.zeros((matched_h, matched_w,3))
	constant = 0
	for i in range(matched_w):
		if i < img0_w - best_shift[0]:
			blending_img[:,i,:] = new_img0[:,i,:]
		elif i >= img0_w:
			blending_img[:,i,:] = new_img1[:,i,:]
		else:
			if i < img0_w - best_shift[0] + constant:
				blending_img[:,i,:] = new_img0[:,i,:]
			elif i >= img0_w - constant:
				blending_img[:,i,:] = new_img1[:,i,:]
			else:
				alpha = (i - img0_w + abs(best_shift[0]))/ abs(best_shift[0])
				for j in range(matched_h):
					if new_img0[j,i,0] == 0:
						blending_img[j,i,:] = new_img1[j,i,:]
					elif new_img1[j,i,0] == 0:
						blending_img[j,i,:] = new_img0[j,i,:]
					else:
						blending_img[j,i,:] = (1-alpha) * new_img0[j,i,:] + alpha * new_img1[j,i,:]
	return blending_img, hh
# cylinder_projection

def cylinder_warping(image, focal_length):
	image_h = image.shape[0]
	image_w = image.shape[1]
	warping = np.zeros(shape = image.shape , dtype=np.uint8)
	h = image_h/2
	w = image_w/2
	for i in range(-int(h), int(h)):
		for j in range(-int(w),int(w)):
			x = int(focal_length*math.atan(j/ focal_length) + w)
			y = int(focal_length*i/math.sqrt(j**2+focal_length**2) + h)
			if x >= 0 and x < image_w and y >= 0 and y < image_h:
				warping[y][x] = image[i+int(h)][j+int(w)]
	_,threshold = cv2.threshold(cv2.cvtColor(warping, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)
	contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	x1, y1, w1, h1 = cv2.boundingRect(contours[0]) 
	return warping[y1:y1+h1, x1:x1+w1]


focal_length = [704.916, 706.286, 705.849, 706.645, 706.587, 705.645, 705.327]
num_of_images  = 7
for i in range(num_of_images):
	image00 = cv2.imread('./parrington/prtn0'+str(i)+'.jpg')
	warping = cylinder_warping(image00, focal_length[i])
	# warping_rgb = warping[:,:,::-1]
	cv2.imwrite('./parrington1/prtn0'+str(i)+'.jpg', warping)
count = 0
for i in range(6,0,-1):
	print(i)
	count+=1
#grayscale_test1photo
	img0 = cv2.imread('./parrington1/prtn0'+str(i)+'.jpg')
	# img0 = cv2.imread('./bridge/DSC_38'+str(i)+'.jpg')
	# cylinder_warping(img00)

	img_gray0 = cv2.cvtColor(img0,cv2.COLOR_BGR2GRAY)
	img_gray0 = np.float32(img_gray0)
	# cv2.imwrite('testgray.jpg', img_gray0)
	print(type(img_gray0), img_gray0.shape)

	 
	corner_response0  = harris(img_gray0, 3, 0.05)
	coords_x0, coords_y0 = supression(corner_response0)

	img1 = cv2.imread('./parrington1/prtn0'+str(i-1)+'.jpg')
	# img1 = cv2.imread('./bridge/DSC_38'+str(i-1)+'.jpg')

	img_gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
	img_gray1 = np.float32(img_gray1)
	# cv2.imwrite('testgray.jpg', img_gray1)
	print(type(img_gray1), img_gray1.shape)


	corner_response1  = harris(img_gray1, 3, 0.05)
	coords_x1, coords_y1 = supression(corner_response1)
	# print(coor_x,coor_y)
	des0 = description(img_gray0, coords_x0, coords_y0, 5)
	des1 = description(img_gray1, coords_x1, coords_y1, 5)

	new_coords_x0,new_coords_y0,new_coords_x1,new_coords_y1 =  matching(des0,des1,coords_x0,coords_y0,coords_x1,coords_y1)
	print(len(new_coords_x0))

# plot_corners(img_gray0, "fig00.png", coords_x1, coords_y1)
# plot_corners(img_gray1, "fig1.png",new_coords_x1, new_coords_y1)
# plot_corners(img_gray0, "fig0.png",new_coords_x0, new_coords_y0)
	# plot_matching(img_gray0, img_gray1, new_coords_x0, new_coords_y0,new_coords_x1,new_coords_y1,"match"+str(i)+".png")
	best_shift = RANSAC(new_coords_x0,new_coords_y0,new_coords_x1,new_coords_y1, 0, 0, 10)
	print("best_shift = ", best_shift)
	if(count == 1):
		blending_img = img0
		pre_h = 0
	blending_img,pre_h = blending(blending_img, img1, best_shift,pre_h)

cv2.imwrite('cvout.jpg',np.array(np.clip(blending_img,0,255),dtype = int))

# crop to ractangle(not yet done)
img = cv2.imread('cvout.jpg')
rows,cols = img.shape[:2]
pts1 = np.float32([[56,65],[238,52],[28,237],[239,240]])
pts2 = np.float32([[0,0],[200,0],[0,200],[200,200]])
M = cv2.getPerspectiveTransform(pts1,pts2)
res = cv2.warpPerspective(img,M,(200,200))
plt.subplot(121)
plt.imshow(img)
plt.show()
plt.axis('off')
plt.subplot(122)
plt.imshow(res)
plt.show()
plt.axis('off')

# plt.imshow(np.array(np.clip(blending_img,0,255),dtype = int))
# plt.savefig("test2.png")
# plt.show()
# plt.axis('off')
# image00 = cv2.imread('./parrington/prtn00.jpg')
# warping = cylinder_warping(image00, 704.696)
# warping_rgb = warping[:,:,::-1]
# plt.imshow(warping_rgb)
# plt.show()
# plt.axis('off')