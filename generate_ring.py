"""
生成圆环 STL：完整环、按等分选择性保留扇区、梯形截面（上下内/外径可不同）。
"""

import argparse
import math


def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    ]


def subtract(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]


def _normalize(v):
    norm = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if norm > 0:
        return [v[0] / norm, v[1] / norm, v[2] / norm]
    return [0, 0, 0]


def _add_quad(faces, a, b, c, d, flip=False):
    """四边形拆成两个三角形，法线朝外（或 flip）。"""
    if flip:
        faces.append([a, c, b])
        faces.append([b, c, d])
    else:
        faces.append([a, b, c])
        faces.append([b, d, c])


def _write_stl_ascii(filename, solid_name, vertices, faces):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"solid {solid_name}\n")
        for face in faces:
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            edge1 = subtract(v2, v1)
            edge2 = subtract(v3, v1)
            normal = _normalize(cross_product(edge1, edge2))
            f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
            f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
            f.write(f"      vertex {v3[0]:.6e} {v3[1]:.6e} {v3[2]:.6e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write(f"endsolid {solid_name}\n")


def normalize(v):
    return _normalize(v)


def generate_ring_stl(
    inner_radius,
    outer_radius,
    height,
    segments=64,
    filename="ring.stl",
    *,
    divisions=1,
    keep_mask=None,
    inner_radius_top=None,
    outer_radius_top=None,
    segments_per_division=None,
    solid_name="ring",
):
    """
    生成圆环 STL。

    参数（内/外径与旧版一致：传入的是直径 mm，内部使用半径）:
    - inner_radius, outer_radius: 底面（z=-h）内径、外径
    - height: 总体高度
    - segments: 当 divisions==1 时，绕整圈划分的段数；divisions>1 且未指定 segments_per_division 时，每份弧段段数约为 max(1, segments // divisions)
    - divisions: 圆周等分数 N（每份圆心角 360/N）
    - keep_mask: 长度 N 的可迭代对象，1/True 保留该份，0/False 去掉；None 表示全部保留
    - inner_radius_top, outer_radius_top: 顶面（z=+h）内径、外径；省略则与底面相同（直圆环）
    - segments_per_division: 每一份保留弧在圆周方向的细分数（>=1），指定时优先于对 segments 的推算

    梯形：顶底内/外径不同时，侧面为圆台（沿母线直线），竖直面封盖仍在径向平面内。
    """
    inner_radius_top = (
        float(inner_radius) if inner_radius_top is None else float(inner_radius_top)
    )
    outer_radius_top = (
        float(outer_radius) if outer_radius_top is None else float(outer_radius_top)
    )

    r_ib = float(inner_radius) / 2.0
    r_ob = float(outer_radius) / 2.0
    r_it = float(inner_radius_top) / 2.0
    r_ot = float(outer_radius_top) / 2.0
    h = float(height) / 2.0

    if r_ib >= r_ob or r_it >= r_ot:
        raise ValueError("内径必须小于外径（顶面与底面均满足）")

    n_div = int(divisions)
    if n_div < 1:
        raise ValueError("divisions 至少为 1")

    if keep_mask is None:
        mask = [True] * n_div
    else:
        mask = [bool(int(x)) for x in keep_mask]
        if len(mask) != n_div:
            raise ValueError(f"keep_mask 长度应为 {n_div}（与 divisions 一致），当前为 {len(mask)}")

    if not any(mask):
        raise ValueError("keep_mask 至少保留一份扇区")

    if n_div == 1 and all(mask) and abs(r_ib - r_it) < 1e-9 and abs(r_ob - r_ot) < 1e-9:
        _generate_ring_cylinder_simple(
            r_ib, r_ob, h, int(segments), filename, solid_name
        )
        return

    if segments_per_division is None:
        spd = max(1, int(segments) // n_div) if n_div > 1 else int(segments)
    else:
        spd = max(1, int(segments_per_division))

    vertices = []
    faces = []

    def pt_outer_top(th):
        return [r_ot * math.cos(th), r_ot * math.sin(th), h]

    def pt_outer_bot(th):
        return [r_ob * math.cos(th), r_ob * math.sin(th), -h]

    def pt_inner_top(th):
        return [r_it * math.cos(th), r_it * math.sin(th), h]

    def pt_inner_bot(th):
        return [r_ib * math.cos(th), r_ib * math.sin(th), -h]

    def append_sector(th_a, th_b, need_wall_lo, need_wall_hi):
        """扇区 [th_a, th_b]（th_b > th_a），是否需要两端径向封盖。"""
        steps = spd
        idx0 = len(vertices)
        for s in range(steps + 1):
            t = s / steps
            th = th_a + t * (th_b - th_a)
            vertices.append(pt_outer_top(th))
            vertices.append(pt_outer_bot(th))
            vertices.append(pt_inner_top(th))
            vertices.append(pt_inner_bot(th))

        def quad_out(s):
            b = idx0 + s * 4
            _add_quad(faces, b + 0, b + 4, b + 5, b + 1)

        def quad_inn(s):
            b = idx0 + s * 4
            faces.append([b + 2, b + 6, b + 3])
            faces.append([b + 6, b + 7, b + 3])

        def quad_top(s):
            b = idx0 + s * 4
            _add_quad(faces, b + 0, b + 4, b + 6, b + 2)

        def quad_bot(s):
            b = idx0 + s * 4
            _add_quad(faces, b + 1, b + 3, b + 7, b + 5, flip=True)

        for s in range(steps):
            quad_out(s)
            quad_inn(s)
            quad_top(s)
            quad_bot(s)

        def radial_cap_wall_at(th, outward_dec_theta):
            """
            在固定角度 th 的径向竖直面上加四边形，法线指向 θ 减小方向一侧（朝空腔）为 outward_dec_theta。
            顶点顺序：外上、内上、内下、外下 → 从“略小于 th”一侧看为顺时针则朝外。
            """
            ot, ob, it, ib = pt_outer_top(th), pt_outer_bot(th), pt_inner_top(th), pt_inner_bot(th)
            base = len(vertices)
            vertices.extend([ot, it, ib, ob])
            if outward_dec_theta:
                _add_quad(faces, base, base + 1, base + 2, base + 3)
            else:
                _add_quad(faces, base, base + 3, base + 2, base + 1, flip=True)

        if need_wall_lo:
            radial_cap_wall_at(th_a, True)
        if need_wall_hi:
            radial_cap_wall_at(th_b, False)

    two_pi = 2 * math.pi
    for k in range(n_div):
        if not mask[k]:
            continue
        th_a = two_pi * k / n_div
        th_b = two_pi * (k + 1) / n_div
        k_lo = (k - 1) % n_div
        k_hi = (k + 1) % n_div
        need_wall_lo = not mask[k_lo]
        need_wall_hi = not mask[k_hi]
        append_sector(th_a, th_b, need_wall_lo, need_wall_hi)

    _write_stl_ascii(filename, solid_name, vertices, faces)

    kept = sum(1 for x in mask if x)
    print(f"STL 已生成: {filename}")
    print(f"等分数: {n_div} | 保留份数: {kept} | 每份弧细分: {spd}")
    print(f"底面 内/外径: {inner_radius}/{outer_radius} mm | 顶面: {inner_radius_top}/{outer_radius_top} mm")
    print(f"高度: {height} mm | 顶点: {len(vertices)} | 三角形面: {len(faces)}")


def _generate_ring_cylinder_simple(r_inner, r_outer, h, segments, filename, solid_name):
    """整圈、上下等径时的原实现。"""
    vertices = []
    faces = []
    outer_top = []
    outer_bottom = []
    inner_top = []
    inner_bottom = []

    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        outer_top.append([r_outer * cos_a, r_outer * sin_a, h])
        outer_bottom.append([r_outer * cos_a, r_outer * sin_a, -h])
        inner_top.append([r_inner * cos_a, r_inner * sin_a, h])
        inner_bottom.append([r_inner * cos_a, r_inner * sin_a, -h])

    vertices.extend(outer_top)
    vertices.extend(outer_bottom)
    vertices.extend(inner_top)
    vertices.extend(inner_bottom)

    vertex_offset = 0
    num_per_circle = segments + 1

    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        outer_v1 = vertex_offset + i
        outer_v2 = vertex_offset + next_i
        inner_v1 = vertex_offset + 2 * num_per_circle + i
        inner_v2 = vertex_offset + 2 * num_per_circle + next_i
        faces.append([outer_v1, outer_v2, inner_v1])
        faces.append([outer_v2, inner_v2, inner_v1])

    bottom_outer_offset = num_per_circle
    bottom_inner_offset = 3 * num_per_circle
    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        outer_v1 = bottom_outer_offset + i
        outer_v2 = bottom_outer_offset + next_i
        inner_v1 = bottom_inner_offset + i
        inner_v2 = bottom_inner_offset + next_i
        faces.append([outer_v1, inner_v1, outer_v2])
        faces.append([outer_v2, inner_v1, inner_v2])

    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        top_v1 = vertex_offset + i
        top_v2 = vertex_offset + next_i
        bottom_v1 = vertex_offset + num_per_circle + i
        bottom_v2 = vertex_offset + num_per_circle + next_i
        faces.append([top_v1, bottom_v1, top_v2])
        faces.append([top_v2, bottom_v1, bottom_v2])

    for i in range(segments):
        next_i = (i + 1) % num_per_circle
        top_v1 = vertex_offset + 2 * num_per_circle + i
        top_v2 = vertex_offset + 2 * num_per_circle + next_i
        bottom_v1 = vertex_offset + 3 * num_per_circle + i
        bottom_v2 = vertex_offset + 3 * num_per_circle + next_i
        faces.append([top_v1, top_v2, bottom_v1])
        faces.append([top_v2, bottom_v2, bottom_v1])

    _write_stl_ascii(filename, solid_name, vertices, faces)

    print(f"STL文件已生成: {filename}")
    print(f"顶点数: {len(vertices)}")
    print(f"面数: {len(faces)}")
    print(f"内半径: {r_inner}mm 外半径: {r_outer}mm 高度: {2 * h}mm")


def _parse_mask(s):
    if not s:
        return None
    parts = s.replace(",", " ").split()
    return [int(p) for p in parts]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="生成圆环 STL（可选等分保留掩码、梯形顶底径）")
    p.add_argument("--inner", type=float, default=65, help="底面内径 mm")
    p.add_argument("--outer", type=float, default=80, help="底面外径 mm")
    p.add_argument("--height", type=float, default=30)
    p.add_argument("--segments", type=int, default=64, help="整圈分段（divisions=1）或用于推算每份细分")
    p.add_argument("--out", default="ring.stl")
    p.add_argument("--divisions", type=int, default=1)
    p.add_argument(
        "--keep",
        type=str,
        default="",
        help='保留掩码，如 "1,0,1,0,1,0" 长度须等于 divisions',
    )
    p.add_argument("--inner-top", type=float, default=None, help="顶面内径 mm（默认同底）")
    p.add_argument("--outer-top", type=float, default=None, help="顶面外径 mm（默认同底）")
    p.add_argument("--spd", type=int, default=None, help="每份弧圆周方向细分段数")
    args = p.parse_args()

    generate_ring_stl(
        args.inner,
        args.outer,
        args.height,
        segments=args.segments,
        filename=args.out,
        divisions=args.divisions,
        keep_mask=_parse_mask(args.keep) if args.keep else None,
        inner_radius_top=args.inner_top,
        outer_radius_top=args.outer_top,
        segments_per_division=args.spd,
    )
