# LICENSE HEADER MANAGED BY add-license-header
#
# Copyright 2018 Kornia Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
import torch

from kornia.geometry.quaternion import Quaternion

from testing.base import assert_close


class TestQuaternion:
    def _make_rand_data(self, device, dtype, batch_size):
        shape = [] if batch_size is None else [batch_size]
        return torch.rand([*shape, 4], device=device, dtype=dtype)

    def assert_close(self, actual, expected, rtol=None, atol=None):
        if isinstance(actual, Quaternion):
            actual = actual.data.data
        elif isinstance(actual, torch.nn.Parameter):
            actual = actual.data
        if isinstance(expected, Quaternion):
            expected = expected.data.data
        elif isinstance(expected, torch.nn.Parameter):
            expected = expected.data

        assert_close(actual, expected, rtol=rtol, atol=atol)

    def test_smoke(self, device, dtype):
        q = Quaternion.from_coeffs(1.0, 0.0, 0.0, 0.0)
        q = q.to(device, dtype)
        q_data = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device, dtype=dtype)
        assert isinstance(q, Quaternion)
        assert q.shape == (4,)
        self.assert_close(q.data, q_data)
        self.assert_close(q.q, q_data)
        self.assert_close(q.real, q_data[..., 0])
        self.assert_close(q.scalar, q_data[..., 0])
        self.assert_close(q.vec, q_data[..., 1:])

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_init(self, device, dtype, batch_size):
        q1 = Quaternion.identity(batch_size, device, dtype)
        q2 = Quaternion(q1.data)
        assert isinstance(q2, Quaternion)
        self.assert_close(q1, q2)

    def test_init_fail(self, device, dtype):
        with pytest.raises(Exception):
            _ = Quaternion("q")

        with pytest.raises(Exception):
            _ = Quaternion([1, 0, 0, 0])

        with pytest.raises(Exception):
            _ = Quaternion(1, [0, 0, 0])

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_random(self, device, dtype, batch_size):
        q = Quaternion.random(batch_size, device, dtype)
        q_n = q.normalize().norm()
        self.assert_close(q_n, q_n.new_ones(q_n.shape))

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_minus(self, device, dtype, batch_size):
        data = self._make_rand_data(device, dtype, batch_size)
        q = Quaternion(data)
        q = q.to(device, dtype)
        self.assert_close(-q, -data)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_add(self, device, dtype, batch_size):
        d1 = self._make_rand_data(device, dtype, batch_size)
        d2 = self._make_rand_data(device, dtype, batch_size)
        q1 = Quaternion(d1)
        q2 = Quaternion(d2)
        q3 = q1 + q2
        assert isinstance(q3, Quaternion)
        self.assert_close(q3, d1 + d2)
        q1 += q2
        self.assert_close(q1, q3)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_subtract(self, device, dtype, batch_size):
        d1 = self._make_rand_data(device, dtype, batch_size)
        d2 = self._make_rand_data(device, dtype, batch_size)
        q1 = Quaternion(d1)
        q2 = Quaternion(d2)
        q3 = q1 - q2
        assert isinstance(q3, Quaternion)
        self.assert_close(q3, d1 - d2)
        q1 -= q2
        self.assert_close(q1, q3)

    def test_multiplication_of_bases(self, device, dtype):
        one = Quaternion.from_coeffs(1.0, 0.0, 0.0, 0.0).to(device, dtype)
        i = Quaternion.from_coeffs(0.0, 1.0, 0.0, 0.0).to(device, dtype)
        j = Quaternion.from_coeffs(0.0, 0.0, 1.0, 0.0).to(device, dtype)
        k = Quaternion.from_coeffs(0.0, 0.0, 0.0, 1.0).to(device, dtype)

        self.assert_close(i * i, j * j)
        self.assert_close(j * j, k * k)
        self.assert_close(k * k, i * j * k)
        self.assert_close(i * j * k, -one)

        self.assert_close(i * j, k)
        self.assert_close(i * i, -one)
        self.assert_close(i * k, -j)
        self.assert_close(j * i, -k)
        self.assert_close(j * j, -one)
        self.assert_close(j * k, i)
        self.assert_close(k * i, j)
        self.assert_close(k * j, -i)
        self.assert_close(k * k, -one)
        self.assert_close(i * j * k, -one)

    def test_division_of_bases(self, device, dtype):
        one = Quaternion.from_coeffs(1.0, 0.0, 0.0, 0.0).to(device, dtype)
        i = Quaternion.from_coeffs(0.0, 1.0, 0.0, 0.0).to(device, dtype)
        j = Quaternion.from_coeffs(0.0, 0.0, 1.0, 0.0).to(device, dtype)
        k = Quaternion.from_coeffs(0.0, 0.0, 0.0, 1.0).to(device, dtype)

        self.assert_close(i / i, j / j)
        self.assert_close(j / j, k / k)
        self.assert_close(k / k, one)
        self.assert_close(k / -k, -one)

        self.assert_close(i / j, -k)
        self.assert_close(i / i, one)
        self.assert_close(i / k, j)
        self.assert_close(j / i, k)
        self.assert_close(j / j, one)
        self.assert_close(j / k, -i)
        self.assert_close(k / i, -j)
        self.assert_close(k / j, i)
        self.assert_close(k / k, one)
        self.assert_close(i / -j, k)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_pow(self, device, dtype, batch_size):
        q = Quaternion.random(batch_size, device, dtype)
        q1 = Quaternion.identity(batch_size, device, dtype)
        self.assert_close(q**0, q1)
        self.assert_close(q**1, q)
        self.assert_close(q**2, q * q)
        self.assert_close(q**-1, q.inv())
        self.assert_close((q**0.5) * (q**0.5), q)
        self.assert_close((q1**1), q1)
        self.assert_close((q1**2), q1)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_inverse(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        q2 = Quaternion.identity(batch_size, device, dtype)
        self.assert_close(q1 * q1.inv(), q2, rtol=1e-4, atol=1e-4)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_conjugate(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        q2 = Quaternion.random(batch_size, device, dtype)
        self.assert_close((q1 * q2).conj(), q2.conj() * q1.conj())

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_double_conjugate(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        self.assert_close(q1, q1.conj().conj())

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_norm(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        q2 = Quaternion.random(batch_size, device, dtype)
        self.assert_close((q1 * q2).norm(), q1.norm() * q2.norm())

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_norm_shape(self, device, dtype, batch_size):
        q = Quaternion.random(batch_size, device, dtype)
        expected_shape = () if batch_size is None else (batch_size,)
        self.assert_close(tuple(q.norm().shape), expected_shape)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_normalize(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        q1_n = q1.normalize().norm()
        self.assert_close(q1_n, q1_n.new_ones(q1_n.shape))

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_matrix(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        m1 = q1.matrix()
        q2 = Quaternion.from_matrix(m1)
        for qq1, qq2 in zip(q1.data, q2.data):
            try:
                self.assert_close(qq1, qq2)
            except Exception:
                self.assert_close(qq1, -qq2)

    @pytest.mark.parametrize("batch_size", (1, 2, 5))
    def test_getitem(self, device, dtype, batch_size):
        q = Quaternion.random(batch_size, device, dtype)
        for i in range(batch_size):
            q1 = q[i]
            self.assert_close(q1.data, q.data[i])

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_axis_angle(self, device, dtype, batch_size):
        q1 = Quaternion.random(batch_size, device, dtype)
        angle = 2 * q1.scalar.arccos()[..., None]
        axis = q1.vec / (angle / 2).sin()
        axis_angle = axis * angle
        q2 = Quaternion.from_axis_angle(axis_angle)
        q2 = q2.to(device, dtype)
        self.assert_close(q1, q2)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_to_axis_angle(self, device, dtype, batch_size):
        # batch_s = 5
        # random_coefs = Quaternion.random(batch_s).data
        random_coefs = torch.tensor(
            [
                [2.5398e-04, -2.2677e-01, -8.3897e-01, 4.9467e-01],
                [-1.7005e-01, -1.0974e-01, 3.7635e-01, -9.0410e-01],
                [9.1273e-01, 4.8935e-02, -6.2994e-03, 4.0558e-01],
                [-9.8316e-01, 5.4078e-03, 1.4471e-01, 1.1145e-01],
                [4.5794e-02, -7.0831e-01, 6.7577e-01, 1.9883e-01],
            ],
            device=device,
            dtype=dtype,
        )

        q = Quaternion(random_coefs)
        axis_angle_actual = q.to_axis_angle()

        axis_angle_expected = torch.tensor(
            [
                [-0.7123, -2.6353, 1.5538],
                [0.3118, -1.0693, 2.5687],
                [0.1008, -0.0130, 0.8356],
                [-0.0109, -0.2911, -0.2242],
                [-2.1626, 2.0632, 0.6071],
            ],
            device=device,
            dtype=dtype,
        )

        self.assert_close(axis_angle_expected, axis_angle_actual, 1e-4, 1e-4)

    @pytest.mark.parametrize("batch_size", (None, 1, 2, 5))
    def test_slerp(self, device, dtype, batch_size):
        for axis in torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]):
            axis = axis.to(device, dtype)
            if batch_size is not None:
                axis = axis.repeat(batch_size, 1)
            q1 = Quaternion.from_axis_angle(axis * 0)
            q1.to(device, dtype)
            q2 = Quaternion.from_axis_angle(axis * 3.14159)
            q2.to(device, dtype)
            for t in torch.linspace(0.1, 1, 10):
                q3 = q1.slerp(q2, t)
                q4 = Quaternion.from_axis_angle(axis * t * 3.14159)
                self.assert_close(q3, q4)

    def test_from_to_euler_values(self, device, dtype):
        # num_samples = 5
        # data = 2 * torch.rand(3, num_samples, device=device, dtype=dtype) - 1
        # roll, pitch, yaw = torch.pi * data
        roll = torch.tensor(
            [2.6518599987, 0.0612506270, 1.2417907715, 2.8829660416, -1.9961174726, 0], device=device, dtype=dtype
        )

        pitch = torch.tensor(
            [2.3267219067, -2.7309591770, -1.4011553526, -2.1962766647, 2.1454355717, 0], device=device, dtype=dtype
        )

        yaw = torch.tensor(
            [-0.8856627345, 0.2605336905, 0.4579202533, -1.3095731735, 0.6096843481, 0], device=device, dtype=dtype
        )

        euler_expected = torch.tensor(
            [
                [-0.4897327125, 0.8148705959, 2.2559301853],
                [-3.0803420544, -0.4106334746, -2.8810589314],
                [1.2417914867, -1.4011553526, 0.4579201937],
                [-0.2586266696, -0.9453159571, 1.8320195675],
                [1.1454752684, 0.9961569905, -2.5319085121],
                [0, 0, 0],
            ],
            device=device,
            dtype=dtype,
        )

        q = Quaternion.from_euler(roll, pitch, yaw)
        euler = q.to_euler()
        euler = torch.stack(euler, -1)

        self.assert_close(euler, euler_expected, 1e-4, 1e-4)
