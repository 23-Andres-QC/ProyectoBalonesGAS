from typing import Any, Dict

import numpy as np

from app.application.ports.tracker import Tracker


class ByteTrackTracker(Tracker):
	"""Minimal IoU-based tracker to provide tracker_id for detections.

	No es un ByteTrack completo, pero mantiene IDs estables
	entre frames para que `supervision.LineZone` pueda contar cruces.
	Solo asocia detecciones con tracks de la misma clase (`class_id`).
	"""

	def __init__(self, iou_threshold: float = 0.4, max_lost: int = 15) -> None:
		"""Initialize simple tracker.

		Args:
			iou_threshold: IoU mínimo para asociar detecciones a tracks existentes.
			max_lost: Número máximo de frames sin ver un track antes de eliminarlo.
		"""
		self._iou_threshold = iou_threshold
		self._max_lost = max_lost
		self._next_id = 0
		# id -> {"bbox": np.ndarray[4], "lost": int, "class_id": int | None}
		self._tracks: Dict[int, Dict[str, Any]] = {}

	def update(self, detections: Any) -> Any:
		"""Update tracks and attach tracker_id to detections.

		Expects `detections` to be `supervision.Detections` (con atributo `xyxy`).
		Si no es compatible, devuelve las detecciones sin modificar.
		"""
		# Degradar con gracia si no es el tipo esperado
		if detections is None or not hasattr(detections, "xyxy"):
			return detections

		bboxes = np.asarray(detections.xyxy)
		n_dets = len(bboxes)
		# class_id puede no existir (según origen de detecciones)
		det_class_ids = getattr(detections, "class_id", None)
		# Sin detecciones: solo envejecer tracks existentes
		if n_dets == 0:
			self._age_tracks()
			# Asegurar atributo tracker_id vacío para coherencia
			setattr(detections, "tracker_id", np.empty((0,), dtype=int))
			return detections

		# Preparar matriz de IDs para las detecciones actuales
		tracker_ids = np.full(shape=(n_dets,), fill_value=-1, dtype=int)

		# Si no hay tracks previos, asignar nuevos IDs a todo
		if not self._tracks:
			for i in range(n_dets):
				tracker_ids[i] = self._new_id()
				self._tracks[int(tracker_ids[i])] = {
					"bbox": bboxes[i].copy(),
					"lost": 0,
					"class_id": int(det_class_ids[i]) if det_class_ids is not None else None,
				}
			setattr(detections, "tracker_id", tracker_ids)
			return detections

		# Hay tracks previos: calcular IoU y hacer matching greedy
		track_ids = list(self._tracks.keys())
		track_bboxes = np.stack([self._tracks[t_id]["bbox"] for t_id in track_ids])
		track_classes = np.array([
			self._tracks[t_id].get("class_id", None) for t_id in track_ids
		])
		iou_matrix = self._compute_iou_matrix(track_bboxes, bboxes, track_classes, det_class_ids)

		# Matching greedy por IoU descendente
		used_tracks = set()
		used_dets = set()
		flat_indices = np.dstack(np.unravel_index(np.argsort(-iou_matrix, axis=None), iou_matrix.shape))[0]
		for t_idx, d_idx in flat_indices:
			if iou_matrix[t_idx, d_idx] < self._iou_threshold:
				break
			if t_idx in used_tracks or d_idx in used_dets:
				continue
			track_id = track_ids[t_idx]
			tracker_ids[d_idx] = track_id
			self._tracks[track_id]["bbox"] = bboxes[d_idx].copy()
			self._tracks[track_id]["lost"] = 0
			used_tracks.add(t_idx)
			used_dets.add(d_idx)

		# Crear nuevos tracks para detecciones no emparejadas
		for d_idx in range(n_dets):
			if d_idx in used_dets:
				continue
			new_id = self._new_id()
			tracker_ids[d_idx] = new_id
			self._tracks[new_id] = {
				"bbox": bboxes[d_idx].copy(),
				"lost": 0,
				"class_id": int(det_class_ids[d_idx]) if det_class_ids is not None else None,
			}

		# Envejecer tracks que no se usaron en este frame
		for idx, track_id in enumerate(track_ids):
			if idx in used_tracks:
				continue
			self._tracks[track_id]["lost"] += 1
			if self._tracks[track_id]["lost"] > self._max_lost:
				del self._tracks[track_id]

		setattr(detections, "tracker_id", tracker_ids)
		return detections

	def _new_id(self) -> int:
		track_id = self._next_id
		self._next_id += 1
		return track_id

	def _age_tracks(self) -> None:
		"""Increment lost counter for all tracks and drop stale ones."""
		for track_id in list(self._tracks.keys()):
			self._tracks[track_id]["lost"] += 1
			if self._tracks[track_id]["lost"] > self._max_lost:
				del self._tracks[track_id]

	def _compute_iou_matrix(
		self,
		tracks: np.ndarray,
		dets: np.ndarray,
		track_classes: np.ndarray,
		det_classes: Any,
	) -> np.ndarray:
		"""Compute IoU matrix between track boxes and detection boxes.

		Si `det_classes` está disponible, solo se considera IoU para
		pares track/detección con la misma clase; el resto queda en 0.
		"""
		T = tracks.shape[0]
		D = dets.shape[0]
		iou = np.zeros((T, D), dtype=float)
		for t in range(T):
			tx1, ty1, tx2, ty2 = tracks[t]
			track_area = max(0.0, tx2 - tx1) * max(0.0, ty2 - ty1)
			for d in range(D):
				# Si tenemos clases en ambos lados y no coinciden, IoU=0
				if det_classes is not None and track_classes[t] is not None:
					if int(track_classes[t]) != int(det_classes[d]):
						continue
				dx1, dy1, dx2, dy2 = dets[d]
				det_area = max(0.0, dx2 - dx1) * max(0.0, dy2 - dy1)
				ix1 = max(tx1, dx1)
				iy1 = max(ty1, dy1)
				ix2 = min(tx2, dx2)
				iy2 = min(ty2, dy2)
				w = max(0.0, ix2 - ix1)
				h = max(0.0, iy2 - iy1)
				inter = w * h
				union = track_area + det_area - inter
				iou[t, d] = inter / union if union > 0 else 0.0
		return iou
