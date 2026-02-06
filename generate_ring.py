"""
生成圆环STL模型
内径: 65mm, 外径: 80mm, 高度: 30mm
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

def generate_ring_stl(inner_radius, outer_radius, height, segments=64, filename='ring.stl'):
    """
    生成圆环STL模型
    
    参数:
    - inner_radius: 内径 (mm)
    - outer_radius: 外径 (mm)
    - height: 高度 (mm)
    - segments: 圆周分段数（越多越平滑）
    - filename: 输出文件名
    """
    # 计算半径
    r_inner = inner_radius / 2.0
    r_outer = outer_radius / 2.0
    h = height / 2.0  # 高度的一半（从中心到顶部/底部）
    
    vertices = []
    faces = []
    
    # 生成顶部和底部的圆环顶点
    # 外圆顶点
    outer_top = []
    outer_bottom = []
    inner_top = []
    inner_bottom = []
    
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 外圆顶部和底部
        outer_top.append([r_outer * cos_a, r_outer * sin_a, h])
        outer_bottom.append([r_outer * cos_a, r_outer * sin_a, -h])
        
        # 内圆顶部和底部
        inner_top.append([r_inner * cos_a, r_inner * sin_a, h])
        inner_bottom.append([r_inner * cos_a, r_inner * sin_a, -h])
    
    # 添加顶点到列表
    vertices.extend(outer_top)
    vertices.extend(outer_bottom)
    vertices.extend(inner_top)
    vertices.extend(inner_bottom)
    
    vertex_offset = 0
    num_per_circle = segments + 1
    
    # 生成顶部面（外圆和内圆之间的圆环）
    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        
        # 外圆到内圆的四边形，分成两个三角形
        # 外圆顶点索引
        outer_v1 = vertex_offset + i
        outer_v2 = vertex_offset + next_i
        # 内圆顶点索引
        inner_v1 = vertex_offset + 2 * num_per_circle + i
        inner_v2 = vertex_offset + 2 * num_per_circle + next_i
        
        # 第一个三角形（外圆 -> 内圆）
        faces.append([outer_v1, outer_v2, inner_v1])
        # 第二个三角形
        faces.append([outer_v2, inner_v2, inner_v1])
    
    # 生成底部面
    bottom_outer_offset = num_per_circle
    bottom_inner_offset = 3 * num_per_circle
    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        
        # 外圆顶点索引
        outer_v1 = bottom_outer_offset + i
        outer_v2 = bottom_outer_offset + next_i
        # 内圆顶点索引
        inner_v1 = bottom_inner_offset + i
        inner_v2 = bottom_inner_offset + next_i
        
        # 第一个三角形（注意顺序，从底部看是逆时针）
        faces.append([outer_v1, inner_v1, outer_v2])
        # 第二个三角形
        faces.append([outer_v2, inner_v1, inner_v2])
    
    # 生成外侧面（外圆顶部到底部的圆柱面）
    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        
        # 顶部外圆顶点
        top_v1 = vertex_offset + i
        top_v2 = vertex_offset + next_i
        # 底部外圆顶点
        bottom_v1 = vertex_offset + num_per_circle + i
        bottom_v2 = vertex_offset + num_per_circle + next_i
        
        # 第一个三角形
        faces.append([top_v1, bottom_v1, top_v2])
        # 第二个三角形
        faces.append([top_v2, bottom_v1, bottom_v2])
    
    # 生成内侧面（内圆顶部到底部的圆柱面，注意法向量方向）
    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        
        # 顶部内圆顶点
        top_v1 = vertex_offset + 2 * num_per_circle + i
        top_v2 = vertex_offset + 2 * num_per_circle + next_i
        # 底部内圆顶点
        bottom_v1 = vertex_offset + 3 * num_per_circle + i
        bottom_v2 = vertex_offset + 3 * num_per_circle + next_i
        
        # 第一个三角形（注意顺序，内侧面法向量朝内）
        faces.append([top_v1, top_v2, bottom_v1])
        # 第二个三角形
        faces.append([top_v2, bottom_v2, bottom_v1])
    
    # 写入STL文件（ASCII格式）
    with open(filename, 'w') as f:
        f.write('solid ring\n')
        
        for face in faces:
            # 获取三个顶点
            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            
            # 计算法向量
            edge1 = subtract(v2, v1)
            edge2 = subtract(v3, v1)
            normal = cross_product(edge1, edge2)
            normal = normalize(normal)
            
            # 写入面
            f.write(f'  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n')
            f.write('    outer loop\n')
            f.write(f'      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n')
            f.write(f'      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n')
            f.write(f'      vertex {v3[0]:.6e} {v3[1]:.6e} {v3[2]:.6e}\n')
            f.write('    endloop\n')
            f.write('  endfacet\n')
        
        f.write('endsolid ring\n')
    
    print(f'STL文件已生成: {filename}')
    print(f'顶点数: {len(vertices)}')
    print(f'面数: {len(faces)}')
    print(f'内径: {inner_radius}mm (内半径: {r_inner}mm)')
    print(f'外径: {outer_radius}mm (外半径: {r_outer}mm)')
    print(f'高度: {height}mm')

if __name__ == '__main__':
    # 生成圆环STL模型
    # 内径65mm, 外径80mm, 高30mm
    generate_ring_stl(
        inner_radius=65,
        outer_radius=80,
        height=30,
        segments=64,
        filename='ring.stl'
    )
