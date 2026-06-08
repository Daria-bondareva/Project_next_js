"use client";

import { useState, useEffect } from "react";
import styles from "./TagSelectionModal.module.css";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onSave: (selectedTags: string[]) => void;
  initialSelected: string[];
  allTags: string[];
  title?: string;
};

export default function TagSelectionModal({
  isOpen,
  onClose,
  onSave,
  initialSelected,
  allTags,
  title = "Вибір тегів"
}: Props) {
  const [tempSelected, setTempSelected] = useState<string[]>([]);

  useEffect(() => {
    if (isOpen) {
      setTempSelected([...initialSelected]);
    }
  }, [isOpen, initialSelected]);

  const toggleTag = (tag: string) => {
    setTempSelected(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleSave = () => {
    onSave(tempSelected);
    onClose();
  };

  if (!isOpen) return null;

  const availableTags = allTags.filter(tag => !tempSelected.includes(tag));

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <h2 className={styles.modalHeader}>{title}</h2>

        <div className={styles.selectionArea}>
          <div className={`${styles.sectionBox} ${styles.selectedBox}`}>
            <p className={styles.sectionTitle}>✅ Вибрані</p>
            <div className={styles.tagList}>
              {tempSelected.length === 0 && (
                <span style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>Пусто...</span>
              )}
              {tempSelected.map(tag => (
                <Badge key={tag} variant="selected" onClick={() => toggleTag(tag)}>
                  {tag} ✕
                </Badge>
              ))}
            </div>
          </div>

          <div className={styles.sectionBox}>
            <p className={styles.sectionTitle}>➕ Доступні</p>
            <div className={styles.tagList}>
              {availableTags.map(tag => (
                <Badge key={tag} variant="outline" onClick={() => toggleTag(tag)}>
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        <div className={styles.modalActions}>
          <Button variant="secondary" onClick={onClose}>Відмінити</Button>
          <Button variant="primary" onClick={handleSave}>Зберегти</Button>
        </div>
      </div>
    </div>
  );
}
