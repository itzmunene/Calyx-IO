# Calyx - Design Specification Document
**Version 1.0 | iOS Mobile Application**

---

## 1. Product Overview

### 1.1 Product Name
**Calyx** - Your Personal Flower Discovery & Documentation App

### 1.2 Product Vision
Calyx is a mobile application that empowers users to discover, identify, and curate their own digital herbarium of flowers. Whether you're a gardening enthusiast, botanist, or nature lover, Calyx makes it easy to search for flowers, save your favorites, and build a personalized catalog of discoveries.

### 1.3 Target Platform
- **Primary Platform**: iOS (iPhone)
- **Minimum iOS Version**: iOS 15.0+
- **Device Support**: iPhone (optimized for iPhone 12 and newer)
- **Future Platform**: Android (Phase 2)

### 1.4 Core Value Proposition
- Quick and accurate flower search functionality
- Personal documentation and cataloging system
- Secure user authentication
- Search history tracking
- Beautiful, nature-inspired interface

---

## 2. User Personas

### Primary Persona: The Garden Enthusiast
- **Age**: 28-55
- **Goals**: Document flowers in their garden, learn about new species, plan future plantings
- **Pain Points**: Forgetting flower names, losing track of plants they've seen, difficulty organizing plant information

### Secondary Persona: The Nature Explorer
- **Age**: 22-45
- **Goals**: Identify flowers on hikes, build a collection of discovered species
- **Pain Points**: Can't identify flowers in the wild, no way to remember discoveries

---

## 3. Feature Specifications

### 3.1 User Authentication

#### Sign Up / Sign In (OAuth)
- **Primary Authentication Methods**:
  - Sign in with Apple
  - Sign in with Google
  - Sign in with Facebook
- **Required Setup After OAuth**:
  - Display name
  - Unique username (alphanumeric + underscores, 3-20 characters)
  - Profile photo (optional, can use OAuth provider photo)
  - Profile about (one sentence, max 80 characters)
- **Username Validation**:
  - Check for uniqueness
  - No special characters except underscore
  - Case-insensitive storage but preserves display preference
- **Success Flow**: 
  - First-time users: Username creation screen → Onboarding
  - Returning users: Direct to home screen
- **Security**:
  - Email hidden from other users (stored privately)
  - OAuth tokens securely stored
  - Biometric authentication option (Face ID/Touch ID)

#### No Password Management Needed
- OAuth providers handle password security
- Users manage passwords through Google/Facebook/Apple

### 3.2 Flower Search

#### Search Interface
- **Search Input**:
  - Prominent search bar on home screen
  - Auto-complete suggestions as user types
  - Search by common name or scientific name
  - Voice search capability (optional Phase 2)

#### Search Methods
1. **Text Search**: Direct search by flower name
2. **Filter Search**: 
   - By color
   - By bloom season
   - By region/climate
   - By plant type (annual, perennial, etc.)

#### Search Results
- **Display Format**:
  - Grid view (default) or List view toggle
  - **Polaroid Frame Design**:
    - Each result card styled as a vintage Polaroid
    - White border around image (thicker bottom for Polaroid aesthetic)
    - Flower name displayed in "handwritten" style font below image (within Polaroid)
    - Scientific name in smaller italic text
    - Subtle shadow for depth
  - Quick "Save" button (heart icon) in top right corner of Polaroid
- **Image Optimization for Smooth Scrolling**:
  - Progressive image loading (blur-up technique)
  - Thumbnail size: 400x400px for grid view
  - Image compression: WebP format with JPEG fallback
  - Lazy loading: Images load as they enter viewport
  - Preload next batch (20 items) when user scrolls to 80% of current results
  - Cache images locally for instant re-display
  - Low network handling:
    - Show lower resolution preview immediately
    - Load high-res in background
    - Skeleton loading placeholders with Polaroid frame
- **Sorting Options**:
  - Relevance (default)
  - Alphabetical (A-Z)
  - Most popular
  - Most interactions (new)
- **Pagination**: Load 20 results at a time with infinite scroll
  - Smooth scroll performance even on slow networks
  - Loading indicator: Subtle animated flower icon at bottom

#### Flower Detail View
When user taps on a search result:
- **Hero image**: Large, high-quality flower photo in Polaroid frame style
- **Back button** (top left)
- **Share button** (top right)
- **Scroll for information**:
  - Common name (large, bold)
  - Scientific name (italic, below)
  - Tabbed sections: Overview, Care, Details, Community
  
**Overview Tab**:
  - Family classification
  - Description (origin, characteristics)
  - **Scent description** (new):
    - Fragrance profile (floral, citrus, sweet, earthy, etc.)
    - Intensity level (subtle, moderate, strong)
    - User-contributed scent notes
  - Growing conditions (light, water, soil)
  - Bloom time
  - Height/spread
  - Hardiness zones

**Care Tab**:
  - Detailed care tips
  - Common problems & solutions
  - Best practices

**Details Tab**:
  - Botanical information
  - Native region
  - Additional characteristics

**Community Tab** (new):
  - **Comments Section**:
    - User profile photo, username, timestamp
    - Comment text
    - Upvote button with count (visible)
    - Downvote button (hidden count, affects sorting only)
    - Reply functionality (nested comments)
  - **Filtering Options**:
    - Most interactions (upvotes - downvotes, default)
    - Newest first
    - Oldest first
  - **Comment Actions**:
    - Report inappropriate comments
    - Edit own comments (within 5 minutes)
    - Delete own comments
  - **Engagement**:
    - "Add a comment" input field at bottom
    - Character limit: 500 characters
    - Optional: Attach photo from user's own flower photos

- **Action buttons** (sticky footer):
  - Save to Collection (prominent, primary button)
  - Like/Unlike (heart icon with count)
  - Share (iOS share sheet)

### 3.3 Search History (Catalog Tab)

#### Features
- **Automatic tracking**: All searches automatically saved with timestamp
- **Display**:
  - Chronological list (newest first)
  - Group by date (Today, Yesterday, This Week, Earlier)
  - Each entry shows:
    - Flower thumbnail
    - Flower name
    - Search date/time
    - Quick access to flower details
- **Management**:
  - Swipe to delete individual searches
  - "Clear All" option (with confirmation dialog)
  - Search within history

#### Data Retention
- History stored locally and synced to user account
- No automatic deletion (user-controlled)

### 3.4 Saved Flowers Tab

#### Features
- **Personal Collection**: User-curated list of saved flowers
- **Display Options**:
  - Grid view (2 columns with images)
  - List view (with thumbnail + name)
- **Organization**:
  - Create custom collections/folders (e.g., "My Garden", "Wish List", "Spring Blooms")
  - Drag and drop to reorder
  - Bulk selection for moving to collections
- **Each Saved Flower Includes**:
  - All original flower information
  - Personal notes field (editable)
  - Date saved
  - Optional: Photo upload capability for user's own photos of the flower
  - Tags (custom user tags)

#### Actions
- Remove from saved
- Share individual flower or entire collection
- Export collection as PDF

### 3.5 User Profile

#### Profile Information
- **Profile Header** (minimalist, clean design):
  - **Layout**:
    - Profile photo (left side, circular, 80pt diameter)
    - **Catalogue count** (next to profile photo):
      - Number displayed prominently
      - Label: "Flowers"
      - Counts total unique flowers across saved + collections (no duplicates)
    - **Text section** (right side):
      - Display name (bold, 18pt)
      - Username (below, @username format, 14pt, medium gray)
      - Profile about (one sentence, max 80 characters, 14pt regular)
  
- **Privacy Controls**:
  - Toggle: Make catalogue public/private
  - Favorites are always public
  - Individual collections can be set to public/private
  - Private content only visible to user

- **Profile Sections** (with divider, then tabs):
  - **Collections Tab**:
    - Grid of user's collections
    - Each shows: Cover photo (first flower), name, flower count
    - Public/private indicator icon
    - Tap to view collection details
  - **Catalogue Tab** (new):
    - All saved flowers in one unified view
    - Polaroid grid display
    - Filter by: All, Public only, Private only
    - Shows total unique flower count
  - **Favorites Tab**:
    - Quick access to favorited/liked flowers
    - Always public
    - Polaroid grid display

- **Member info**:
  - Member since date (small text at bottom)
  - Email hidden from all users (stored privately)

#### Settings
- Account settings
  - Email preferences (notifications)
  - Delete account
  - Manage OAuth connections
- App settings
  - Notifications toggle
  - Default view preference (grid/list)
  - Measurement units (metric/imperial)
- Privacy
  - Default collection privacy (public/private)
  - Data export
  - Clear cache
- About
  - App version
  - Terms of service
  - Privacy policy
  - Help & support

### 3.6 Social Features (New)

#### Following System
- **Follow/Unfollow Users**:
  - Button on user profiles
  - Following count & followers count visible on profiles
  - View list of who you're following
  - View list of your followers
  - Privacy: Users can make their follower/following lists private

#### Collection Interactions
- **Like Collections**:
  - Heart icon on collection cards
  - Like count visible
  - View who liked a collection (if public)
- **Save Others' Collections**:
  - "Save to Library" button on public collections
  - Saved collections appear in your profile under "Saved Collections" section
  - Original creator credited
  - Updates sync: If creator adds flowers, your saved copy updates too
  - Can create your own copy to modify independently

#### Discovery Feed
- Users discover collections through:
  - Following feed (collections from users you follow)
  - Explore page (popular/trending collections)
  - Search (search by collection name or username)

#### Notifications
- New follower notifications
- Someone liked your collection
- Someone saved your collection
- Someone commented on a flower in your collection (optional)

---

## 4. Information Architecture

### 4.1 Navigation Structure

**Bottom Tab Bar Navigation (Apple Floating Glass Design)**:
- **Visual Style**: Translucent frosted glass effect (iOS glassmorphism)
- **Material**: UIBlurEffect with vibrancy
- **Appearance**: Floating above content, rounded corners, subtle shadow
- **Adaptive**: Adjusts opacity and blur based on content beneath

**Tabs** (4 total):

1. **Home** (House icon)
   - **Content**: Curated feed of flower catalogues
   - **Algorithm**: 
     - Mix of flowers from users you follow (60%)
     - Flowers from users with similar collections (30%)
     - Random discover content (10%)
   - **Display**: Polaroid-style cards with username, flower info
   - **Interactions**: Like, save, view full details, visit user profile
   - **Refresh**: Pull to refresh for new content

2. **Catalog/Search** (Magnifying glass icon)
   - **Primary**: Search bar at top (glassy design matching tab bar)
   - **Below search**: Search history
     - Chronological list (newest first)
     - Group by date (Today, Yesterday, This Week, Earlier)
     - Each entry: Thumbnail, flower name, timestamp
     - Swipe to delete individual items
     - "Clear All" option
   - **When searching**: Results replace history view
   - **Empty state**: Suggested searches or trending flowers

3. **Saved** (Bookmark icon)
   - **Top section**: Glassy tab switcher between:
     - Saved Flowers (all saved items)
     - Collections (organized groups)
   - **Saved Flowers view**: 
     - Polaroid grid of all saved flowers
     - Sort/filter options
   - **Collections view**:
     - Grid of collection cards
     - Each shows cover, name, count, privacy icon
     - Tap to view collection contents

4. **Profile** (Person icon)
   - User profile view
   - Settings access
   - Personal stats and collections

### 4.2 Screen Hierarchy

```
├── Authentication
│   ├── Welcome/Landing
│   ├── Sign In
│   ├── Sign Up
│   └── Password Reset
│
├── Home (Search)
│   ├── Search Results
│   └── Flower Detail
│       ├── Save Confirmation
│       └── Add Notes
│
├── Catalog (History)
│   └── Flower Detail (from history)
│
├── Saved Flowers
│   ├── Collections View
│   ├── Collection Detail
│   └── Flower Detail (from saved)
│       └── Edit Notes
│
└── Profile
    ├── Edit Profile
    ├── Settings
    ├── Help & Support
    └── About
```

---

## 5. User Flows

### 5.1 First-Time User Flow
1. Download app from App Store
2. Open app → See welcome screen with app benefits
3. Tap "Get Started" → Sign Up screen
4. Create account (email, password, name)
5. Optional: Brief onboarding tutorial (swipeable cards)
6. Land on Home screen (Search)

### 5.2 Search & Save Flow
1. User on Home screen
2. Tap search bar → Keyboard appears
3. Type flower name (e.g., "rose")
4. See auto-complete suggestions
5. Tap suggestion or press search
6. View search results (grid of flowers)
7. Tap a flower → Flower detail view
8. Read information
9. Tap "Save" button → Saved confirmation + option to add to collection
10. Flower added to Saved tab
11. Search automatically added to Catalog tab

### 5.3 Browse Saved Flowers Flow
1. User taps Saved tab
2. See grid of saved flowers
3. Option to filter by collection
4. Tap a flower → View details with personal notes
5. Edit notes if desired
6. Return to Saved list

---

## 6. Technical Specifications

### 6.1 Technology Stack Recommendations

#### Frontend
- **Framework**: SwiftUI (modern, declarative UI)
- **Minimum iOS**: 15.0
- **Languages**: Swift 5.5+

#### Backend
- **API**: RESTful API or GraphQL
- **Authentication**: JWT tokens + OAuth 2.0
- **Database**: 
  - User data: PostgreSQL or MongoDB
  - Flower database: PostgreSQL with full-text search
- **Cloud Storage**: AWS S3 or Cloudinary for images
- **Hosting**: AWS, Google Cloud, or Firebase

#### Third-Party Services
- **Authentication**: 
  - Sign in with Apple (native)
  - Firebase Auth or Auth0 for Google/Facebook OAuth
  - Biometric authentication support (Face ID/Touch ID)
- **Analytics**: Firebase Analytics or Mixpanel
- **Crash Reporting**: Firebase Crashlytics or Sentry
- **Push Notifications**: Firebase Cloud Messaging or APNs
- **Image CDN**: Cloudinary or Imgix (for optimization and transformations)
- **Moderation**: Content moderation API for comments (e.g., OpenAI Moderation API)

### 6.2 Data Models

#### User Model
```
User {
  id: UUID
  email: String (unique, indexed, hidden from other users)
  username: String (unique, indexed, 3-20 chars, alphanumeric + underscore)
  displayName: String
  profilePhotoURL: String?
  profileAbout: String? (max 80 chars)
  oauthProvider: String (apple/google/facebook)
  oauthId: String (unique per provider)
  createdAt: DateTime
  lastLoginAt: DateTime
  cataloguePrivacy: Boolean (public/private, default: public)
  followerCount: Integer (denormalized)
  followingCount: Integer (denormalized)
  preferences: UserPreferences
}

UserPreferences {
  defaultView: String (grid/list)
  measurementUnit: String (metric/imperial)
  notificationsEnabled: Boolean
  emailNotifications: Boolean
  defaultCollectionPrivacy: Boolean (public/private)
}
```

#### Flower Model
```
Flower {
  id: UUID
  commonName: String
  scientificName: String
  family: String
  description: String
  imageURLs: [String]
  growingConditions: GrowingConditions
  bloomSeason: [String]
  hardiness: String
  height: String
  spread: String
  careTips: String
  tags: [String]
  scentProfile: ScentProfile (new)
  likeCount: Integer (denormalized)
  commentCount: Integer (denormalized)
}

ScentProfile {
  fragranceTypes: [String] (floral, citrus, sweet, earthy, spicy, etc.)
  intensity: String (none, subtle, moderate, strong)
  userNotes: [String] (community-contributed descriptions)
}

GrowingConditions {
  light: String (full sun, partial shade, shade)
  water: String (low, medium, high)
  soilType: String
  pH: String
}
```

#### Comment Model (New)
```
Comment {
  id: UUID
  flowerId: UUID (foreign key)
  userId: UUID (foreign key)
  content: String (max 500 chars)
  photoURL: String? (optional user photo attachment)
  upvotes: Integer
  downvotes: Integer (hidden from display)
  score: Integer (upvotes - downvotes, for sorting)
  parentCommentId: UUID? (for nested replies)
  createdAt: DateTime
  editedAt: DateTime?
  isEdited: Boolean
}
```

#### SavedFlower Model
```
SavedFlower {
  id: UUID
  userId: UUID (foreign key)
  flowerId: UUID (foreign key)
  savedAt: DateTime
  collectionId: UUID? (foreign key)
  personalNotes: String?
  userPhotos: [String]?
  tags: [String]?
  isPublic: Boolean (default: inherits from collection or user catalogue privacy)
}
```

#### SearchHistory Model
```
SearchHistory {
  id: UUID
  userId: UUID (foreign key)
  flowerId: UUID (foreign key)
  searchQuery: String
  searchedAt: DateTime
}
```

#### Collection Model
```
Collection {
  id: UUID
  userId: UUID (foreign key)
  name: String
  description: String?
  coverImageURL: String? (first flower image)
  createdAt: DateTime
  updatedAt: DateTime
  isPublic: Boolean (default: user preference)
  flowerCount: Integer (computed)
  likeCount: Integer (denormalized)
  saveCount: Integer (denormalized, how many users saved this collection)
}
```

#### Follow Model (New)
```
Follow {
  id: UUID
  followerId: UUID (foreign key to User)
  followingId: UUID (foreign key to User)
  createdAt: DateTime
}
```

#### CollectionLike Model (New)
```
CollectionLike {
  id: UUID
  collectionId: UUID (foreign key)
  userId: UUID (foreign key)
  likedAt: DateTime
}
```

#### SavedCollection Model (New)
```
SavedCollection {
  id: UUID
  originalCollectionId: UUID (foreign key to Collection)
  userId: UUID (foreign key to User, who saved it)
  savedAt: DateTime
  syncWithOriginal: Boolean (default: true)
}
```

### 6.3 API Endpoints

#### Authentication (OAuth)
- `POST /auth/oauth/apple` - Sign in with Apple
- `POST /auth/oauth/google` - Sign in with Google
- `POST /auth/oauth/facebook` - Sign in with Facebook
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/username` - Set/update username (one-time after OAuth)

#### Flowers
- `GET /flowers/search?query={text}&filters={}` - Search flowers
- `GET /flowers/:id` - Get flower details
- `GET /flowers/feed` - Get personalized home feed
- `GET /flowers/trending` - Get trending flowers
- `PUT /flowers/:id/scent` - Add user scent note (community contribution)

#### Comments (New)
- `POST /flowers/:flowerId/comments` - Add comment to flower
- `GET /flowers/:flowerId/comments?filter={interactions|newest|oldest}` - Get comments
- `PUT /comments/:id` - Edit own comment (within 5 min)
- `DELETE /comments/:id` - Delete own comment
- `POST /comments/:id/upvote` - Upvote comment
- `POST /comments/:id/downvote` - Downvote comment (hidden)
- `DELETE /comments/:id/upvote` - Remove upvote
- `DELETE /comments/:id/downvote` - Remove downvote
- `POST /comments/:id/report` - Report inappropriate comment

#### Saved Flowers
- `POST /saved` - Save a flower
- `GET /saved` - Get all saved flowers for user
- `PUT /saved/:id` - Update saved flower (notes, tags)
- `DELETE /saved/:id` - Remove saved flower
- `GET /saved/collections/:collectionId` - Get flowers in collection

#### Collections
- `POST /collections` - Create new collection
- `GET /collections` - Get all user collections
- `GET /collections/:id` - Get collection details
- `PUT /collections/:id` - Update collection (name, description, privacy)
- `DELETE /collections/:id` - Delete collection
- `POST /collections/:id/like` - Like a collection
- `DELETE /collections/:id/like` - Unlike a collection
- `POST /collections/:id/save` - Save someone else's collection
- `DELETE /collections/:id/save` - Unsave a collection
- `GET /collections/:id/likes` - Get users who liked collection
- `GET /collections/discover` - Discover public collections

#### Social/Following (New)
- `POST /users/:userId/follow` - Follow a user
- `DELETE /users/:userId/follow` - Unfollow a user
- `GET /users/:userId/followers` - Get user's followers
- `GET /users/:userId/following` - Get who user follows
- `GET /users/:userId/profile` - Get public profile
- `GET /users/username/:username` - Find user by username

#### Search History
- `GET /history` - Get search history
- `DELETE /history/:id` - Delete history item
- `DELETE /history/clear` - Clear all history

#### User Profile
- `GET /user/profile` - Get own profile
- `PUT /user/profile` - Update profile (display name, about, photo)
- `PUT /user/privacy` - Update privacy settings
- `DELETE /user/account` - Delete account
- `GET /user/stats` - Get user statistics
- `GET /user/notifications` - Get notifications
- `PUT /user/notifications/:id/read` - Mark notification as read

### 6.4 Performance Requirements
- App launch time: < 2 seconds (cold start)
- Search results: < 1 second response time
- Image loading: Progressive loading with placeholders
- Offline capability: Cache recent searches and saved flowers
- Data sync: Background sync when online

### 6.5 Security Requirements
- HTTPS for all API communications
- Password hashing: bcrypt with salt
- JWT token expiration: 24 hours
- Refresh token expiration: 30 days
- Biometric authentication storage in iOS Keychain
- Input validation and sanitization
- Rate limiting on API endpoints
- GDPR compliance for data export/deletion

---

## 7. UI/UX Design Guidelines

### 7.1 Design Philosophy
Calyx should feel organic, fresh, and botanical while maintaining modern iOS design standards. The interface should be clean, allowing the beautiful flower imagery to take center stage.

### 7.2 Color Palette

**Primary Colors**:
- **Botanical Green**: #2D5016 (primary actions, accents)
- **Sage Green**: #8FA888 (secondary elements)
- **Cream**: #F5F1E8 (backgrounds)
- **Earth Brown**: #6B4423 (text, grounding elements)

**Accent Colors**:
- **Petal Pink**: #E8B4B8 (saved/favorited items)
- **Sky Blue**: #A8C5DA (informational elements)
- **Soft Yellow**: #F4E4C1 (highlights, warnings)

**Neutral Colors**:
- **White**: #FFFFFF
- **Light Gray**: #F0F0F0 (card backgrounds)
- **Medium Gray**: #C4C4C4 (borders, dividers)
- **Dark Gray**: #4A4A4A (body text)
- **Black**: #1A1A1A (headings)

### 7.3 Typography

**Primary Font**: SF Pro (iOS system font)
- **Display/Headings**: SF Pro Display
  - H1: 28pt, Bold
  - H2: 22pt, Semibold
  - H3: 18pt, Semibold
- **Body Text**: SF Pro Text
  - Body: 16pt, Regular
  - Small: 14pt, Regular
  - Caption: 12pt, Regular
- **Scientific Names**: SF Pro Text, Italic, 14pt

### 7.4 Iconography
- Use SF Symbols for consistency with iOS
- Custom botanical line icons for unique features
- Icon style: Rounded, organic shapes
- Icon colors: Align with color palette

### 7.5 Spacing & Layout
- **Base unit**: 8pt grid system
- **Screen margins**: 16pt (left/right)
- **Card padding**: 16pt
- **Element spacing**: 8pt, 16pt, 24pt, 32pt
- **Corner radius**: 
  - Cards: 12pt
  - Buttons: 8pt
  - Input fields: 8pt

### 7.6 Key Screen Designs

#### Welcome/Landing Screen
- Full-screen botanical background (subtle, not overwhelming)
- App logo centered
- Tagline: "Discover. Save. Grow Your Flower Knowledge"
- Three OAuth buttons (Apple, Google, Facebook)
- Apple design language: Rounded, prominent buttons
- Minimalist design

#### Home (Feed) Screen
- **Apple Floating Glass Tab Bar** at bottom
- **Content**: Curated feed of flower discoveries
- **Each card** (Polaroid style):
  - Username at top with small profile photo
  - Large flower photo in Polaroid frame
  - Flower name in "handwritten" font on Polaroid bottom
  - Like button, save button, comment count
  - Timestamp
- **Interactions**: Pull to refresh (smooth animation)
- **Scroll**: Infinite scroll, smooth performance

#### Catalog/Search Screen
- **Glassy search bar** at top (matching tab bar aesthetic)
  - Frosted glass effect
  - Search icon left, voice search right
  - Rounded corners, subtle shadow
- **Below search**: Search history
  - Grouped by date (collapsible sections)
  - Each item: Small Polaroid thumbnail, name, time
  - Swipe left to delete (iOS standard)
- **Search results** (when active):
  - 2-column Polaroid grid
  - Smooth infinite scroll with image optimization

#### Search Results Screen
- Search query displayed in glassy header
- View toggle (grid/list) in top right corner
- Filter button with bottom sheet options
- Results in **Polaroid grid**:
  - White border around each image
  - Thicker bottom border (Polaroid style)
  - Flower name in handwritten font
  - Scientific name in smaller italic
  - Heart icon for quick save (top right corner)
- Pull to refresh

#### Flower Detail Screen
- **Hero image**: Large Polaroid-framed photo at top
- Back button (top left, glassy circle)
- Share button (top right, glassy circle)
- **Tabs below hero** (glassy tab bar):
  - Overview | Care | Details | Community
- **Content scrolls** within selected tab
- **Sticky footer** (glassy):
  - "Save to Collection" button (primary)
  - Like button with count
  - Share button

#### Saved Flowers Screen
- **Header**: "Saved" title
- **Glassy tab switcher** (top, below header):
  - "Flowers" tab | "Collections" tab
  - Smooth sliding animation
- **Flowers view**: 
  - Polaroid grid (2 columns)
  - Each card shows flower with name
  - Filter/sort in top right (glassy button)
- **Collections view**:
  - Larger cards showing collection cover
  - Name, count, privacy icon overlay
  - Like count if collection is liked

#### Profile Screen (Minimalist & Clean)
- **Profile Header**:
  - **Left**: Circular profile photo (80pt)
  - **Center**: Catalogue count
    - Large number (32pt, bold)
    - "Flowers" label below (12pt)
  - **Right**: Text stack
    - Display name (18pt, bold)
    - @username (14pt, gray)
    - Profile about (14pt, regular, one line)
- **Follower/Following counts** (below header, centered):
  - Two numbers side by side
  - "X Followers  •  Y Following"
  - Tappable to view lists
- **Divider line** (subtle, 1pt gray)
- **Glassy tab bar** (Collections | Catalogue | Favorites):
  - Smooth transitions
  - Content loads below tabs
- **Collections tab**: Grid of collection cards
- **Catalogue tab**: All unique flowers (Polaroid grid)
- **Favorites tab**: Favorited items (Polaroid grid)
- **Settings icon** (top right corner, gear icon)

#### Other User Profile Screen
- Similar layout to own profile
- **Follow/Unfollow button** below header (prominent)
- Shows only public content
- Catalogue only visible if user has it set to public
- Message button (future feature placeholder)

### 7.7 Animations & Interactions
- **Transitions**: Smooth, natural (0.3s duration)
- **Button press**: Subtle scale down (0.95)
- **Pull to refresh**: Organic loading indicator (flower blooming animation)
- **Save action**: Heart icon animation (scale + color change)
- **Image loading**: Fade-in with blur effect
- **Tab switching**: Crossfade transition

### 7.8 Component Library

**Apple Glassmorphism Elements**:
- **Tab Bar**:
  - Background: UIBlurEffect (systemMaterial)
  - Vibrancy: High
  - Corner radius: 24pt
  - Padding: 12pt vertical
  - Position: Floating 16pt from bottom, 16pt from sides
  - Shadow: 0pt 8pt 24pt rgba(0,0,0,0.15)
- **Search Bar (Glassy)**:
  - Background: UIBlurEffect (systemThinMaterial)
  - Border: 1pt white with 20% opacity
  - Corner radius: 22pt (fully rounded)
  - Height: 44pt
  - Shadow: 0pt 2pt 8pt rgba(0,0,0,0.1)
- **Floating Buttons**:
  - Background: UIBlurEffect (systemUltraThinMaterial)
  - Size: 44x44pt (circular)
  - Icon: White or primary color
  - Shadow: 0pt 4pt 12pt rgba(0,0,0,0.15)

**Polaroid Cards**:
- **Frame Design**:
  - White background
  - Border: 12pt padding all sides
  - Bottom border: 32pt (for text space)
  - Drop shadow: 0pt 4pt 12pt rgba(0,0,0,0.12)
  - Slight rotation: Random -2° to +2° for organic feel
- **Image**: 
  - Aspect ratio: 1:1 (square)
  - Fit: Cover (no distortion)
- **Text area** (bottom 32pt):
  - Flower name: "Recoleta" or handwritten-style font, 16pt
  - Scientific name: SF Pro Italic, 12pt, gray
- **Interaction**:
  - Tap: Slight scale (0.98) + navigation
  - Long press: Quick action menu

**Buttons**:
- Primary: Filled, botanical green background, white text
- Secondary: Outlined, botanical green border, green text
- Tertiary: Text only, botanical green text
- Glassy: Frosted background (systemThinMaterial), white text
- Height: 48pt (adequate touch target)

**Input Fields**:
- Border: 1pt medium gray
- Focus state: 2pt botanical green border with glow
- Placeholder: Medium gray text
- Error state: Red border with error message below
- Glassy variant: Frosted background with subtle border

**Cards** (Standard, non-Polaroid):
- Background: White or light gray
- Border: None (use shadow only)
- Shadow: 0pt 2pt 12pt rgba(0,0,0,0.08)
- Corner radius: 12pt
- Padding: 16pt

**Tab Bars** (Content sections):
- Style: Segmented control or pills
- Active: Botanical green background, white text
- Inactive: Transparent, gray text
- Glassy variant: Frosted background
- Animation: Smooth sliding indicator (0.3s ease)

---

## 8. Accessibility

### 8.1 Requirements
- **VoiceOver Support**: All elements properly labeled
- **Dynamic Type**: Support for user font size preferences
- **Color Contrast**: WCAG AA compliance (4.5:1 for text)
- **Touch Targets**: Minimum 44x44pt for all interactive elements
- **Alternative Text**: All images have descriptive alt text
- **Keyboard Navigation**: Full app usable with external keyboard
- **Reduced Motion**: Respect user's reduced motion preference

---

## 9. Onboarding Experience

### 9.1 First-Time User Tutorial (Optional Skip)
**Screen 1**: "Discover Thousands of Flowers"
- Visual: Beautiful flower grid
- Text: Search by name, color, or season

**Screen 2**: "Build Your Personal Collection"
- Visual: Saved flowers interface
- Text: Save favorites and organize into collections

**Screen 3**: "Track Your Journey"
- Visual: History/catalog view
- Text: Automatically keep track of every flower you explore

**Screen 4**: "Ready to Start?"
- Call to action button: "Explore Flowers"

---

## 10. Future Enhancements (Phase 2+)

### 10.1 Potential Features
- **Image Recognition**: Take a photo to identify flowers (AI-powered)
- **Advanced Social**: 
  - Direct messaging between users
  - Share flowers/collections to social media
  - Collaborative collections
  - User badges and achievements
- **Garden Planner**: Visual garden layout tool with spacing recommendations
- **Care Reminders**: Push notifications for watering, fertilizing based on saved flowers
- **Offline Mode**: Download flower database for offline browsing
- **AR Preview**: See how flowers look in your space using AR
- **Location Features**:
  - Nearby gardens/nurseries
  - Geo-tagged flower discoveries
  - Regional flower recommendations
- **Bloom Tracking**: Calendar to track when saved flowers bloom in your garden
- **Shopping Integration**: 
  - Links to purchase seeds/plants
  - Price comparison
  - Nursery reviews
- **Widget**: iOS home screen widget showing:
  - Flower of the day
  - Recently saved flowers
  - Quick search access
- **Apple Watch App**: 
  - Quick flower identification
  - Care reminders on wrist
- **Advanced Analytics**:
  - Garden statistics
  - Seasonal insights
  - Collection trends
- **Educational Content**:
  - Flower care courses
  - Seasonal guides
  - Expert tips from botanists

---

## 11. Success Metrics

### 11.1 Key Performance Indicators (KPIs)
- **User Acquisition**: 
  - New sign-ups per month
  - App Store conversion rate
  - OAuth provider breakdown (which is most popular)
- **Engagement**:
  - Daily active users (DAU)
  - Monthly active users (MAU)
  - Average session duration
  - Searches per user per session
  - Feed scroll depth
  - Time spent on flower details
- **Social Engagement** (New):
  - Follow rate (% of users who follow others)
  - Average follows per user
  - Collection likes per day
  - Collections saved per day
  - Comments per flower per day
  - User-to-user interactions
- **Content**:
  - Flowers saved per user
  - Collections created per user
  - Public vs private collection ratio
  - User-generated scent notes
  - Comment quality (upvote ratio)
- **Retention**:
  - Day 1, 7, 30 retention rates
  - Churn rate
  - Return visit frequency
- **Feature Usage**:
  - % of users with saved flowers
  - Average number of saved flowers per user
  - Collection creation rate
  - Search history usage
  - Feed engagement rate
  - Profile view rate

### 11.2 User Satisfaction
- App Store rating goal: 4.5+ stars
- In-app feedback/rating prompts
- User surveys (quarterly)

---

## 12. Launch Strategy

### 12.1 MVP (Minimum Viable Product) - Phase 1
**Must-Have Features for Launch**:
- OAuth authentication (Apple, Google, Facebook sign-in)
- Username creation and profile setup
- Home feed with personalized flower content
- Flower search functionality (with Polaroid grid display)
- Search history (catalog tab)
- Save flowers with privacy controls
- Collections with public/private settings
- User profiles with catalogue count
- Follow/unfollow users
- Like and save others' collections
- Flower detail view with tabs (Overview, Care, Details, Community)
- Comments on flowers with upvote/downvote
- Scent descriptions and community notes
- Apple glassmorphism UI throughout
- Basic notifications (followers, likes, comments)

**Timeline**: 4-5 months development

### 12.2 Beta Testing
- Internal testing: 2 weeks
- Closed beta (TestFlight): 50-100 users, 3-4 weeks
- Collect feedback and iterate
- Bug fixes and performance optimization

### 12.3 App Store Preparation
- App Store listing copy
- Screenshots and preview video
- Keywords optimization for ASO (App Store Optimization)
- Privacy policy and terms of service

---

## 13. Maintenance & Support

### 13.1 Post-Launch
- Monitor crash reports and fix critical bugs (within 24-48 hours)
- Weekly analytics review
- Monthly feature updates
- Quarterly major updates
- User support email: support@calyxapp.com

### 13.2 Content Updates
- Flower database updates: Monthly new additions
- Seasonal featured flowers
- Content accuracy reviews

---

## 14. Legal & Compliance

### 14.1 Required Documentation
- Privacy Policy (GDPR, CCPA compliant)
- Terms of Service
- Data retention policy
- Cookie policy (if web version exists)

### 14.2 Data Protection
- User consent for data collection
- Right to export data
- Right to delete account and all data
- Transparent data usage policies

### 14.3 Content Licensing
- Ensure all flower images are properly licensed
- Attribution for botanical information sources
- Copyright compliance

---

## 15. Appendix

### 15.1 Glossary
- **Hardiness Zone**: Geographic areas defined by climate conditions
- **Perennial**: Plant that lives for more than two years
- **Annual**: Plant that completes its life cycle in one growing season
- **Calyx**: The sepals of a flower, typically forming a protective layer (app namesake)

### 15.2 References
- iOS Human Interface Guidelines
- USDA Plant Database
- Royal Horticultural Society
- Material Design (for Android future development)

### 15.3 Contact
- **Project Owner**: [Your Name]
- **Project Start Date**: February 2026
- **Document Version**: 1.0
- **Last Updated**: February 2, 2026

---

**End of Design Specification**
