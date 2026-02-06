"""
使用轮廓的一半（8个点）绕y轴旋转360度生成旋转体STL模型
"""

import math

def cross_product(v1, v2):
    """计算两个向量的叉积"""
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def subtract(v1, v2):
    """向量减法"""
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def normalize(v):
    """向量归一化"""
    norm = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if norm > 0:
        return [v[0]/norm, v[1]/norm, v[2]/norm]
    return [0, 0, 0]

def generate_revolution_stl_half(profile_points, segments=128, filename='tray_half.stl'):
    """
    使用轮廓的一半绕y轴旋转360度生成旋转体STL模型
    
    参数:
    - profile_points: 轮廓点列表，格式为 [(x, z), ...]，绕y轴旋转
    - segments: 圆周分段数（越多越平滑）
    - filename: 输出文件名
    """
    vertices = []
    faces = []
    
    num_profile_points = len(profile_points)
    num_rotation_segments = segments
    
    # 生成所有顶点
    for i in range(num_rotation_segments + 1):
        angle = 2 * math.pi * i / num_rotation_segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 对每个轮廓点进行旋转
        for j, (x, z) in enumerate(profile_points):
            # 绕y轴旋转：x' = x*cos, z' = x*sin, y' = z
            x_rotated = x * cos_a
            z_rotated = x * sin_a
            y_coord = z  # y轴对应原来的z坐标
            
            vertices.append([x_rotated, y_coord, z_rotated])
    
    # 生成面
    # 对于360度旋转，最后一个旋转段连接到第一个旋转段
    for i in range(num_rotation_segments):
        for j in range(num_profile_points - 1):
            # 检查当前轮廓段的两个点是否都在旋转轴上
            x1 = profile_points[j][0]
            x2 = profile_points[j + 1][0]
            
            # 如果两个点都在旋转轴上（x=0），旋转后会形成一条线，不是面，跳过
            if abs(x1) < 0.001 and abs(x2) < 0.001:
                continue
            
            # 当前旋转段的索引
            curr_ring_start = i * num_profile_points
            # 下一个旋转段：最后一个旋转段连接到第一个旋转段
            if i == num_rotation_segments - 1:
                next_ring_start = 0  # 连接到第一个旋转段
            else:
                next_ring_start = (i + 1) * num_profile_points
            
            # 当前轮廓段的两个点
            v1_idx = curr_ring_start + j
            v2_idx = curr_ring_start + j + 1
            v3_idx = next_ring_start + j
            v4_idx = next_ring_start + j + 1
            
            # 第一个三角形 - 确保从外部看是逆时针
            faces.append([v1_idx, v2_idx, v3_idx])
            # 第二个三角形
            faces.append([v2_idx, v4_idx, v3_idx])
    
    # 写入STL文件（ASCII格式）
    with open(filename, 'w') as f:
        f.write('solid tray\n')
        
        for face in faces:
            # 获取三个顶点
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            
            # 检查是否是退化三角形（三个顶点中有两个相同或共线）
            edge1 = subtract(v2, v1)
            edge2 = subtract(v3, v1)
            normal = cross_product(edge1, edge2)
            normal_len = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
            
            # 如果法线长度为0或非常小，说明是退化三角形，跳过
            if normal_len < 0.0001:
                continue
            
            normal = normalize(normal)
            
            # 计算面的中心点
            center = [
                (v1[0] + v2[0] + v3[0]) / 3.0,
                (v1[1] + v2[1] + v3[1]) / 3.0,
                (v1[2] + v2[2] + v3[2]) / 3.0
            ]
            
            # 对于绕y轴旋转的旋转体，法线应该指向外部（远离旋转轴）
            # 计算从旋转轴到面的中心点的方向
            to_center_x = center[0]
            to_center_z = center[2]
            dist_from_axis_sq = to_center_x**2 + to_center_z**2
            
            # 如果面不在旋转轴上，检查法线方向
            if dist_from_axis_sq > 0.0001:
                dist_from_axis = math.sqrt(dist_from_axis_sq)
                
                # 归一化从旋转轴到中心的方向向量
                dir_to_center_x = to_center_x / dist_from_axis
                dir_to_center_z = to_center_z / dist_from_axis
                
                # 计算法线在xz平面的投影长度
                normal_xz_len_sq = normal[0]**2 + normal[2]**2
                
                if normal_xz_len_sq > 0.0001:
                    # 法线有x或z分量，检查是否指向外部
                    normal_xz_len = math.sqrt(normal_xz_len_sq)
                    normal_xz_x = normal[0] / normal_xz_len
                    normal_xz_z = normal[2] / normal_xz_len
                    
                    # 计算点积：如果为负，说明法线指向内部
                    dot = dir_to_center_x * normal_xz_x + dir_to_center_z * normal_xz_z
                    if dot < 0:
                        # 法线指向内部，反转法线和顶点顺序
                        normal = [-normal[0], -normal[1], -normal[2]]
                        v1, v2, v3 = v1, v3, v2
            
            # 写入面
            f.write(f'  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n')
            f.write('    outer loop\n')
            f.write(f'      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n')
            f.write(f'      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n')
            f.write(f'      vertex {v3[0]:.6e} {v3[1]:.6e} {v3[2]:.6e}\n')
            f.write('    endloop\n')
            f.write('  endfacet\n')
        
        f.write('endsolid tray\n')
    
    print(f'STL文件已生成: {filename}')
    print(f'顶点数: {len(vertices)}')
    print(f'面数: {len(faces)}')
    print(f'轮廓点数: {num_profile_points}')
    print(f'旋转分段数: {num_rotation_segments}')

if __name__ == '__main__':
    # 定义轮廓的一半（8个点）
    profile_points = [
        (0, 0),
        (-35, 0),
        (-35, 5),
        (-25, 5),
        (-25, 20),
        (-20, 20),
        (-20, 10),
        (0, 10)
    ]
    
    # 生成旋转体STL模型（360度旋转）
    generate_revolution_stl_half(
        profile_points=profile_points,
        segments=128,
        filename='tray_half.stl'
    )
