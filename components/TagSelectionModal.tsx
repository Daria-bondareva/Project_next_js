"use client";

import { useState, useEffect } from "react";
import styles from "./TagSelectionModal.module.css"; // Зараз створимо цей CSS

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

  // Коли вікно відкривається, завантажуємо поточні вибрані теги
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
            {/* Ячейка 1: Вибрані */}
            <div className={`${styles.sectionBox} ${styles.selectedBox}`}>
                <p className={styles.sectionTitle}>✅ Вибрані</p>
                <div className={styles.tagList}>
                    {tempSelected.length === 0 && <span style={{color:'#aaa'}}>Пусто...</span>}
                    {tempSelected.map(tag => (
                        <span 
                            key={tag} 
                            onClick={() => toggleTag(tag)}
                            className={`${styles.interactiveTag} ${styles.selectedTag}`}
                        >
                            {tag} ✕
                        </span>
                    ))}
                </div>
            </div>

            {/* Ячейка 2: Доступні */}
            <div className={styles.sectionBox}>
                <p className={styles.sectionTitle}>➕ Доступні</p>
                <div className={styles.tagList}>
                    {availableTags.map(tag => (
                        <span 
                            key={tag} 
                            onClick={() => toggleTag(tag)}
                            className={`${styles.interactiveTag} ${styles.availableTag}`}
                        >
                            {tag}
                        </span>
                    ))}
                </div>
            </div>
        </div>

        <div className={styles.modalActions}>
            <button onClick={onClose} className={styles.cancelBtn}>Відмінити</button>
            <button onClick={handleSave} className={styles.saveBtn}>Зберегти</button>
        </div>
      </div>
    </div>
  );
}