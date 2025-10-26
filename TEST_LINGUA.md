# 🧪 Testing Guide for Lingua Cultural Snapshot

## ✅ All Files Created and Syntax Verified

### Backend Files:
- ✅ `backend/agents/content_feed.py` - Content feed agent
- ✅ `backend/agents/trivia.py` - Trivia agent  
- ✅ `backend/app.py` - API endpoints added

### Frontend Files:
- ✅ `frontend/src/components/CulturalSnapshot.js` - 3-panel layout
- ✅ `frontend/src/components/TriviaPanel.js` - Trivia system
- ✅ `frontend/src/components/VoiceBoxPlaceholder.js` - Voice icon
- ✅ `frontend/src/components/cards/MovieCard.js`
- ✅ `frontend/src/components/cards/NewsCard.js`
- ✅ `frontend/src/components/cards/MusicCard.js`
- ✅ `frontend/src/components/cards/FoodCard.js`
- ✅ `frontend/src/components/cards/AttractionCard.js`
- ✅ `frontend/src/CulturalSnapshotPage.js` - Entry page

---

## 🚀 How to Test

### 1. Start Backend
```bash
cd backend
python app.py
```
Should see: `Running on http://127.0.0.1:5001/`

### 2. Start Frontend (New Terminal)
```bash
cd frontend
npm start
```
Should open: `http://localhost:3000`

### 3. Add CulturalSnapshotPage to Routing

Add this to your App.js:

```javascript
import CulturalSnapshotPage from './CulturalSnapshotPage';

// In your component:
const [view, setView] = useState('main'); // 'main' or 'snapshot'

// Toggle button to test:
<button onClick={() => setView('snapshot')}>
  Test Cultural Snapshot
</button>

{view === 'snapshot' && <CulturalSnapshotPage />}
```

Or create a direct route in `index.js`:

```javascript
import CulturalSnapshotPage from './CulturalSnapshotPage';

// Replace the default render with:
ReactDOM.render(
  <CulturalSnapshotPage />,
  document.getElementById('root')
);
```

---

## 🧪 Manual API Testing

### Test Content Feed Endpoint:
```bash
curl -X POST http://localhost:5001/api/content-feed \
  -H "Content-Type: application/json" \
  -d '{"country": "Japan", "interests": ["movies", "news", "music"]}'
```

### Test Trivia Endpoint:
```bash
curl -X POST http://localhost:5001/api/trivia \
  -H "Content-Type: application/json" \
  -d '{
    "country": "Japan",
    "content_cards": [{"type": "movie", "title": "Test Movie"}]
  }'
```

---

## ✅ Expected Behavior

1. Enter country in CulturalSnapshotPage
2. Select interests (optional)
3. Click "Explore Culture"
4. See 3 panels:
   - **Left**: Scrollable content cards (min 7)
   - **Middle**: Trivia quiz (25 questions, queue-based)
   - **Right**: Voice icon placeholder
5. Answer trivia questions
6. Wrong answers move to end of queue
7. Complete all 25 correctly → Trophy screen!

---

## 📝 Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend compiles without errors  
- [ ] /api/content-feed returns cards
- [ ] /api/trivia returns 25 questions
- [ ] Three panels display correctly
- [ ] Content cards scroll
- [ ] Trivia questions display one at a time
- [ ] Wrong answers go to end of queue
- [ ] Completion screen shows when done
- [ ] All 7+ cards are unique (no duplicates)

---

## 🐛 Known Issues

- **Circular Import Warning**: Pre-existing in backend, doesn't affect new endpoints
- **Integration Data**: Currently returns placeholder data (need real API connections)

---

## ✨ Ready to Test!

Everything is built and ready. Just start the backend and frontend, then access the CulturalSnapshotPage!

