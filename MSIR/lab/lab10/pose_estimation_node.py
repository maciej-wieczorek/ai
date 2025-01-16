import os
import glob
import cv2
import time
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge

class PoseEstimationNode(Node):
    def __init__(self):
        super().__init__('pose_estimation_node')

        # Parameters
        self.image_topic = '/camera/image_raw'
        self.pose_topic = '/pose_estimation'
        self.frame_id = 'camera_frame'
        self.camera_matrix = np.array([[756.5851373, 0.0, 379.08488597],
                                        [0.0, 756.97985199, 504.40192496],
                                        [0.0, 0.0, 1.0]])
        self.dist_coeffs = np.array([0.08922526, -0.14665822, 0.00273984, -0.00156946])

        # ROS publishers
        self.image_pub = self.create_publisher(Image, '/annotated_image', 10)
        self.pose_pub = self.create_publisher(PoseStamped, self.pose_topic, 10)

        # Bridge for OpenCV and ROS
        self.bridge = CvBridge()

        # Process data
        self.process_dataset()

    def process_dataset(self):
        """Load dataset and process each image."""
        dataset_path = '/root/ros2_ws/src/mikrofala_dataset/'      
        image_files = sorted(glob.glob(os.path.join(dataset_path, "*.jpg")))
        points_files = sorted(glob.glob(os.path.join(dataset_path, "*.txt")))

        while True:
            for img_file, pts_file in zip(image_files, points_files):
                image = cv2.imread(img_file)
                keypoints_2d = self.load_keypoints(pts_file)
                # print(keypoints_2d)

                # Draw keypoints on the image
                for x, y in keypoints_2d:
                    cv2.circle(image, (int(x), int(y)), 5, (0, 255, 0), -1)

                # Solve PnP
                keypoints_3d = self.define_3d_points()
                success, rvec, tvec = cv2.solvePnP(
                    keypoints_3d, keypoints_2d, self.camera_matrix, self.dist_coeffs
                )

                if success:
                    pose_msg = self.create_pose_message(rvec, tvec)
                    self.pose_pub.publish(pose_msg)
                    self.get_logger().info('Pose published.')

                # Publish annotated image
                annotated_image = self.bridge.cv2_to_imgmsg(image, encoding='bgr8')
                self.image_pub.publish(annotated_image)
                time.sleep(4)

    def convert_to_keypoints_2d(self, data_str):
        img_width = 750
        img_height = 1000
        
        values = list(map(float, data_str.split()))
    
        # Extract the bounding box info (x, y, width, height)
        x, y, width, height = values[1:5]
        
        # Extract the normalized px, py values
        px_py_values = values[5:]  # Skip the first 5 elements (class-index, x, y, width, height)
        
        # Convert normalized coordinates to pixel coordinates within the image
        keypoints_2d_normalized = np.array(px_py_values).reshape(-1, 2)
        
        keypoints_2d = keypoints_2d_normalized * [img_width, img_height]     

        return keypoints_2d
    
    def load_keypoints(self, file_path):
        with open(file_path, 'r') as file:
            data_str = file.read()
            return np.array(self.convert_to_keypoints_2d(data_str), dtype=np.float32)

    def define_3d_points(self):
        """Define 3D coordinates of the object (e.g., microwave corners)."""
        width = 0.315  # 31.5 cm
        height = 0.163  # 16.3 cm
        return np.array([
            [0, 0, 0],
            [width, 0, 0],
            [width, height, 0],
            [0, height, 0],
        ], dtype=np.float32)

    def create_pose_message(self, rvec, tvec):
        """Create a PoseStamped message from rotation and translation vectors."""
        pose = PoseStamped()
        pose.header.frame_id = self.frame_id
        pose.header.stamp = self.get_clock().now().to_msg()

        # Convert rotation vector to quaternion
        rotation_matrix, _ = cv2.Rodrigues(rvec)
        quaternion = self.rotation_matrix_to_quaternion(rotation_matrix)

        pose.pose.position.x = tvec[0][0]
        pose.pose.position.y = tvec[1][0]
        pose.pose.position.z = tvec[2][0]
        pose.pose.orientation.x = quaternion[0]
        pose.pose.orientation.y = quaternion[1]
        pose.pose.orientation.z = quaternion[2]
        pose.pose.orientation.w = quaternion[3]

        return pose

    def rotation_matrix_to_quaternion(self, R):
        """Convert a rotation matrix to a quaternion."""
        if R.shape != (3, 3):
            raise ValueError("Input matrix must be 3x3.")
            
        trace = np.trace(R)
        if trace > 0:
            s = np.sqrt(trace + 1.0) * 2
            w = 0.25 * s
            x = (R[2, 1] - R[1, 2]) / s
            y = (R[0, 2] - R[2, 0]) / s
            z = (R[1, 0] - R[0, 1]) / s
        else:
            if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
                s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
                w = (R[2, 1] - R[1, 2]) / s
                x = 0.25 * s
                y = (R[0, 1] + R[1, 0]) / s
                z = (R[0, 2] + R[2, 0]) / s
            elif R[1, 1] > R[2, 2]:
                s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
                w = (R[0, 2] - R[2, 0]) / s
                x = (R[0, 1] + R[1, 0]) / s
                y = 0.25 * s
                z = (R[1, 2] + R[2, 1]) / s
            else:
                s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
                w = (R[1, 0] - R[0, 1]) / s
                x = (R[0, 2] + R[2, 0]) / s
                y = (R[1, 2] + R[2, 1]) / s
                z = 0.25 * s
        
        return np.array([w, x, y, z])


def main(args=None):
    rclpy.init(args=args)
    node = PoseEstimationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

