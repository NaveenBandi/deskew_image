## Import necessary Libraries

import numpy as np
from skimage import io
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.transform import hough_line, hough_line_peaks, rotate
import os
from pathlib import Path

def max_freq_elem(peaks_values):
	frequency = {}
	for peak in peaks_values:
		if peak in frequency:
			frequency[peak] += 1
		else:
			frequency[peak] = 1

	sorted_keys = sorted(frequency.keys(), key=frequency.get, reverse=True)
	maximum_frequency = frequency[sorted_keys[0]]

	maximum_array = []
	for sorted_key in sorted_keys:
		if frequency[sorted_key] == maximum_frequency:
			maximum_array.append(sorted_key)

	return maximum_array


def compare_sum(value):
	# return boolean value
	return 44<=value<=46


def calculate_deviation(angle):
	angle_in_degrees = np.abs(angle)
	deviation = np.abs(np.pi /4 -angle_in_degrees)

	return deviation


class deskew_image:
	def __init__(self, image_path):
		self.image_path = image_path


	def preprocess(self):
		## read input image
		self.image = io.imread(self.image_path)
		self.grayscale = rgb2gray(self.image)

	def find_angle(self):
		self.edges = canny(self.grayscale, sigma=3.0)
		self.output, self.angles, self.distances = hough_line(self.edges)

		_, angles_peaks, _ = hough_line_peaks(self.output, self.angles, self.distances , num_peaks=20)
		absolute_deviations = [calculate_deviation(k) for k in angles_peaks]
		average_deviation = np.mean(np.rad2deg(absolute_deviations))
		angles_peaks_degree = [np.rad2deg(x) for x in angles_peaks]

		bin_0_45 = []
		bin_45_90 = []
		bin_0_45n = []
		bin_45_90n = []

		for angle in angles_peaks_degree:

		    deviation_sum = int(90 - angle + average_deviation)
		    if compare_sum(deviation_sum):
		        bin_45_90.append(angle)
		        continue

		    deviation_sum = int(angle + average_deviation)
		    if compare_sum(deviation_sum):
		        bin_0_45.append(angle)
		        continue

		    deviation_sum = int(-angle + average_deviation)
		    if compare_sum(deviation_sum):
		        bin_0_45n.append(angle)
		        continue

		    deviation_sum = int(90 + angle + average_deviation)
		    if compare_sum(deviation_sum):
		        bin_45_90n.append(angle)

		angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
		nb_angles_max = 0
		max_angle_index = -1
		for angle_index, angle in enumerate(angles):
		    nb_angles = len(angle)
		    if nb_angles > nb_angles_max:
		        nb_angles_max = nb_angles
		        max_angle_index = angle_index

		if nb_angles_max:
		        ans_arr = max_freq_elem(angles[max_angle_index])
		        angle = np.mean(ans_arr)
		elif angles_peaks_degree:
		    ans_arr = max_freq_elem(angles_peaks_degree)
		    angle = np.mean(ans_arr)
		else:
		    print("1", None, angles, average_deviation, (out, angles, distances))

		if 0 <= angle <= 90:
		    rot_angle = angle - 90
		elif -45 <= angle < 0:
		    rot_angle = angle - 90
		elif -90 <= angle < -45:
		    rot_angle = 90 + angle

		self.rotation_angle = rot_angle


	def rotate(self):
		self.rotated_image = rotate(self.image, self.rotation_angle, resize=True) * 255


	def save_image(self, path):
		self.save_path = path
		io.imsave(path, self.rotated_image.astype(np.uint8))

root_path = os.getcwd()
image_path = os.path.join(root_path, "law-firm-invoice-template.jpg")
save_path = os.path.join(root_path, "law-firm-invoice-template.jpg")

obj = deskew_image(image_path)
obj.preprocess()
obj.find_angle()
obj.rotate()
obj.save_image(save_path)