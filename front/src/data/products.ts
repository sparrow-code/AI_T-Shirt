import { Product } from '../types/product';

export const products: Product[] = [
  {
    id: 1,
    name: "Cosmic Dreams #1",
    price: 1499,
    rating: 4.8,
    reviews: 124,
    image: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    description: "AI-generated cosmic pattern featuring swirling galaxies and nebulae.",
    sizes: ["S", "M", "L", "XL", "2XL"],
    colors: ["Black", "Navy", "Dark Gray"]
  },
  {
    id: 2,
    name: "Digital Wilderness",
    price: 1699,
    rating: 4.9,
    reviews: 89,
    image: "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    description: "Abstract landscape generated by AI, blending nature with digital artifacts.",
    sizes: ["S", "M", "L", "XL"],
    colors: ["White", "Light Gray", "Sage"]
  },
  {
    id: 3,
    name: "Neural Network",
    price: 1899,
    rating: 4.7,
    reviews: 156,
    image: "https://images.unsplash.com/photo-1527719327859-c6ce80353573?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
    description: "Intricate pattern inspired by neural networks and deep learning.",
    sizes: ["S", "M", "L", "XL", "2XL"],
    colors: ["Black", "White", "Navy"]
  }
];