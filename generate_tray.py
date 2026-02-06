"""
生成旋转体托盘STL模型
横截面轮廓绕y轴旋转生成3D模型
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

def generate_revolution_stl(profile_points, rotation_degrees=360, segments=128, filename='tray.stl'):
    """
    生成旋转体STL模型
    
    参数:
    - profile_points: 横截面轮廓点列表，格式为 [(x, z), ...]，绕y轴旋转
    - rotation_degrees: 旋转角度（度），默认360度
    - segments: 圆周分段数（越多越平滑）
    - filename: 输出文件名
    """
    # 将角度转换为弧度
    rotation_rad = math.radians(rotation_degrees)
    
    vertices = []
    faces = []
    
    num_profile_points = len(profile_points)
    num_rotation_segments = int(segments * rotation_degrees / 360)
    
    # 对于360度旋转，最后一个旋转段和第一个旋转段是同一个位置
    # 所以顶点数应该是 num_rotation_segments + 1（如果360度，最后一个就是第一个）
    # 但对于非360度旋转，需要额外的顶点
    if rotation_degrees >= 360:
        num_vertex_rings = num_rotation_segments + 1  # 360度时，最后一个就是第一个
    else:
        num_vertex_rings = num_rotation_segments + 1  # 非360度也需要额外的顶点
    
    # 生成所有顶点
    for i in range(num_vertex_rings):
        angle = rotation_rad * i / num_rotation_segments
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
    # 对于旋转体，确保所有面的法线指向外部
    # 从外部看，顶点应该是逆时针顺序
    # 
    # 对于180度旋转：
    # - 旋转段0（角度=0）：x从-35到35，z=0
    # - 旋转段N（角度=180）：x从35到-35（反转），z=0
    # - 从外部看（比如从+z方向），顶点顺序应该是逆时针
    for i in range(num_rotation_segments):
        for j in range(num_profile_points):
            # 当前旋转段的索引
            curr_ring_start = i * num_profile_points
            # 下一个旋转段：如果是最后一个旋转段且是360度，则连接到第一个旋转段
            if i == num_rotation_segments - 1 and rotation_degrees >= 360:
                next_ring_start = 0  # 连接到第一个旋转段
            else:
                next_ring_start = (i + 1) * num_profile_points
            
            # 当前轮廓段的两个点（最后一个点和第一个点连接，形成闭合）
            # v1: 当前旋转段的点j
            # v2: 当前旋转段的点j+1
            # v3: 下一个旋转段的点j
            # v4: 下一个旋转段的点j+1
            v1_idx = curr_ring_start + j
            v2_idx = curr_ring_start + ((j + 1) % num_profile_points)
            v3_idx = next_ring_start + j
            v4_idx = next_ring_start + ((j + 1) % num_profile_points)
            
            # 对于旋转体，从外部看应该是逆时针顺序
            # 但是，对于180度旋转，从不同方向看，顺序可能不同
            # 让我们确保：从面的外部看，顶点是逆时针顺序
            # 
            # 对于四边形 v1-v2-v4-v3，分成两个三角形：
            # 三角形1: v1 -> v2 -> v3（从外部看逆时针）
            # 三角形2: v2 -> v4 -> v3（从外部看逆时针）
            # 
            # 但是，我需要确保这个顺序是正确的
            # 让我检查一下：对于旋转体，从外部看，应该是逆时针
            # 如果法线指向外部，那么从外部看应该是逆时针
            faces.append([v1_idx, v2_idx, v3_idx])
            faces.append([v2_idx, v4_idx, v3_idx])
    
    # 写入STL文件（ASCII格式）
    with open(filename, 'w') as f:
        f.write('solid tray\n')
        
        for face in faces:
            # 获取三个顶点
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            
            # 计算面的中心点
            center = [
                (v1[0] + v2[0] + v3[0]) / 3.0,
                (v1[1] + v2[1] + v3[1]) / 3.0,
                (v1[2] + v2[2] + v3[2]) / 3.0
            ]
            
            # 计算法向量（使用右手定则）
            edge1 = subtract(v2, v1)
            edge2 = subtract(v3, v1)
            normal = cross_product(edge1, edge2)
            normal = normalize(normal)
            
            # 使用简单直接的方法：根据面的位置判断法线方向
            # 对于绕y轴旋转的旋转体，法线应该指向外部（远离旋转轴）
            # 
            # 方法：计算从旋转轴到面的中心点的方向，然后检查法线是否与这个方向一致
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
                else:
                    # 法线主要是y方向（水平面）
                    # 对于水平面，法线方向通常已经正确，不需要修正
                    # 顶部面法线向上（y>0），底部面法线向下（y<0）
                    pass
            
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
    print(f'旋转角度: {rotation_degrees}度')
    print(f'轮廓点数: {num_profile_points}')
    print(f'旋转分段数: {num_rotation_segments}')

if __name__ == '__main__':
    # 定义横截面轮廓点（x, z坐标，绕y轴旋转）
    # 按照用户提供的顺序
    profile_points = [
        (-35, 0),
        (-35, 5),
        (-25, 5),
        (-25, 20),
        (-20, 20),
        (-20, 10),
        (20, 10),
        (20, 20),
        (25, 20),
        (25, 5),
        (35, 5),
        (35, 0)
    ]
    
    # 生成旋转体STL模型
    # 沿y轴旋转180度
    generate_revolution_stl(
        profile_points=profile_points,
        rotation_degrees=180,
        segments=128,
        filename='tray.stl'
    )
